"""追溯檢查：規格的編號 → 測試計畫的 TC → 測試程式的 req 標註，三段接不接得起來。

    python scripts/trace.py                    # 印出追溯矩陣與缺口
    python scripts/trace.py --strict           # 有缺口就 exit 1（交付前用）
    python scripts/trace.py --docs examples/it-asset

規則（細節見 templates/TRACEABILITY.md）：
- 「定義」一個編號：寫在標題開頭（### FR-01）、粗體開頭（- **AC-01.1**）、或表格第一欄（| FR-01 |）。
  其他位置出現只算引用。
- 每條 AC / FR / NFR 都要被某個 TC 涵蓋；寫在「不測」段落底下的算刻意不測。
- 每個 TC 都要有測試標註它：@pytest.mark.req("TC-01", ...)。
- 標註裡的編號必須在文件裡定義過。
"""

import argparse
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

ID = r"(?:AC-\d{2,}\.\d+|(?:G|NG|P|EP|US|UC|FR|NFR|ADR|API|UI|TC)-\d{2,})"
ID_RE = re.compile(rf"\b{ID}\b")
HEADING_RE = re.compile(rf"^(#{{1,6}})\s+(?:\*\*)?({ID})\b")
BOLD_RE = re.compile(rf"^\s*(?:[-*]\s+)?\*\*({ID})\*\*")
TABLE_RE = re.compile(rf"^\|\s*(?:\*\*)?({ID})(?:\*\*)?\s*\|")
ANY_HEADING_RE = re.compile(r"^(#{1,6})\s+(.*)")
MARKER_RE = re.compile(r"@pytest\.mark\.req\(([^)]*)\)")
DEF_RE = re.compile(r"^\s*(?:async\s+)?def\s+(\w+)")
QUOTED_RE = re.compile(r"""["']([^"']+)["']""")

NEEDS_TC = ("AC-", "FR-", "NFR-")
NOT_TESTED_WORD = "不測"


@dataclass
class Report:
    defined: set[str] = field(default_factory=set)
    tc_covers: dict[str, set[str]] = field(default_factory=dict)
    exempt: set[str] = field(default_factory=set)
    tests_by_id: dict[str, list[str]] = field(default_factory=dict)
    unknown_refs: list[tuple[str, str]] = field(default_factory=list)

    @property
    def requirements(self) -> list[str]:
        return sorted(i for i in self.defined if i.startswith(NEEDS_TC))

    @property
    def untested_requirements(self) -> list[str]:
        covered = set().union(*self.tc_covers.values()) if self.tc_covers else set()
        return [r for r in self.requirements if r not in covered and r not in self.exempt]

    @property
    def tc_without_tests(self) -> list[str]:
        return sorted(tc for tc in self.tc_covers if tc not in self.tests_by_id)

    @property
    def has_gaps(self) -> bool:
        return bool(self.untested_requirements or self.tc_without_tests or self.unknown_refs)


def _scan_doc(text: str, report: Report) -> None:
    """一行一行讀：記下定義、TC 涵蓋哪些編號、哪些編號在「不測」段落裡。"""
    current_tc: str | None = None
    tc_level = 0
    in_not_tested = False
    not_tested_level = 0

    for line in text.splitlines():
        heading = ANY_HEADING_RE.match(line)
        if heading:
            level = len(heading.group(1))
            if current_tc and level <= tc_level:
                current_tc = None
            if in_not_tested and level <= not_tested_level:
                in_not_tested = False
            if NOT_TESTED_WORD in heading.group(2):
                in_not_tested, not_tested_level = True, level

        defined = HEADING_RE.match(line) or BOLD_RE.match(line) or TABLE_RE.match(line)
        ids_on_line = ID_RE.findall(line)

        if defined:
            new_id = defined.group(defined.lastindex)
            report.defined.add(new_id)
            if new_id.startswith("TC-"):
                report.tc_covers.setdefault(new_id, set())
                others = {i for i in ids_on_line if i != new_id}
                report.tc_covers[new_id] |= others
                if HEADING_RE.match(line):
                    current_tc, tc_level = new_id, len(HEADING_RE.match(line).group(1))
                else:
                    current_tc = None
                continue
            if heading:
                current_tc = None

        if current_tc:
            report.tc_covers[current_tc] |= {i for i in ids_on_line if i != current_tc}
        if in_not_tested:
            report.exempt |= set(ids_on_line)


def _scan_tests(tests_dir: Path, root: Path, report: Report) -> None:
    if not tests_dir.exists():
        return
    for path in sorted(tests_dir.rglob("*.py")):
        rel = path.relative_to(root).as_posix() if path.is_relative_to(root) else path.as_posix()
        pending: list[str] = []
        for line in path.read_text(encoding="utf-8").splitlines():
            marker = MARKER_RE.search(line)
            if marker:
                pending += QUOTED_RE.findall(marker.group(1))
                continue
            func = DEF_RE.match(line)
            if func and pending:
                name = f"{rel}::{func.group(1)}"
                for ref in pending:
                    report.tests_by_id.setdefault(ref, []).append(name)
                    if ref not in report.defined:
                        report.unknown_refs.append((name, ref))
                pending = []


def build_report(docs_dir: Path, tests_dir: Path) -> Report:
    report = Report()
    for doc in sorted(Path(docs_dir).glob("*.md")):
        _scan_doc(doc.read_text(encoding="utf-8"), report)
    root = Path(tests_dir).parent
    _scan_tests(Path(tests_dir), root, report)
    return report


def render(report: Report) -> str:
    lines = ["# 追溯矩陣", "", "| 需求 | 測試案例 | 測試程式 |", "|---|---|---|"]
    for req in report.requirements:
        tcs = sorted(tc for tc, ids in report.tc_covers.items() if req in ids)
        tests = sorted({t for tc in tcs for t in report.tests_by_id.get(tc, [])} | set(report.tests_by_id.get(req, [])))
        tc_cell = "、".join(tcs) or ("（刻意不測）" if req in report.exempt else "❌ 沒有 TC")
        test_cell = "<br>".join(tests) or "—"
        lines.append(f"| {req} | {tc_cell} | {test_cell} |")

    lines += ["", "## 缺口", ""]
    if not report.has_gaps:
        lines.append("沒有缺口：每條需求都有 TC，每個 TC 都有測試。")
    for req in report.untested_requirements:
        lines.append(f"- {req} 沒有任何 TC 涵蓋（寫進 06-test-plan，或放進「不測什麼」並寫理由）")
    for tc in report.tc_without_tests:
        lines.append(f"- {tc} 還沒有測試標註它（@pytest.mark.req(\"{tc}\")）")
    for test, ref in report.unknown_refs:
        lines.append(f"- {test} 標了 {ref}，但文件裡沒有定義這個編號")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="規格 → TC → 測試 的追溯檢查")
    parser.add_argument("--docs", default="docs", help="規格文件資料夾（預設 docs）")
    parser.add_argument("--tests", default="backend/tests", help="測試資料夾（預設 backend/tests）")
    parser.add_argument("--strict", action="store_true", help="有缺口就 exit 1")
    args = parser.parse_args(argv)

    docs = Path(args.docs)
    if not docs.is_dir():
        print(f"找不到規格資料夾 {docs}。D1 的六份文件要放在 docs/ 底下。")
        return 1

    report = build_report(docs, Path(args.tests))
    print(render(report))
    return 1 if args.strict and report.has_gaps else 0


if __name__ == "__main__":
    sys.exit(main())
