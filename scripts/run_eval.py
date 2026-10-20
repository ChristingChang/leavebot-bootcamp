"""AI 功能驗收：把 eval 集逐句打你的解析 API，逐欄比對，算準確率。

    python scripts/run_eval.py                          # 打 http://localhost:8000
    python scripts/run_eval.py --min 0.8                # 低於 80% 就 exit 1
    python scripts/run_eval.py --tags basic,half-day    # 只跑某些標籤

你的 backend 要實作這個合約（LEAVEBOT.md「解析 API 合約」）：

    POST /api/parse   {"sentence": "...", "today": "YYYY-MM-DD"}
    → {"requests": [{"start_date", "end_date", "period", "leave_type", "days"}, ...], "clarify": bool}

回應裡多出來的欄位不影響比對。上線門檻要訂多少，是你們在 06-test-plan.md 自己決定的事。
"""

import argparse
import json
import sys
import urllib.error
import urllib.request
from collections.abc import Callable, Iterable
from dataclasses import dataclass, field
from pathlib import Path

FIELDS = ("start_date", "end_date", "period", "leave_type", "days")
DEFAULT_FIXTURES = Path(__file__).resolve().parents[1] / "fixtures" / "leave-sentences.jsonl"

Post = Callable[[str, str], dict]


@dataclass
class Result:
    total: int = 0
    passed: int = 0
    failures: list[tuple[str, str]] = field(default_factory=list)

    @property
    def accuracy(self) -> float:
        return self.passed / self.total if self.total else 0.0


def _key(request: dict) -> tuple:
    return (str(request.get("start_date")), str(request.get("period")))


def compare(case: dict, response: dict) -> str | None:
    """比對一句。對了回 None；錯了回一句說明哪裡錯。"""
    if not isinstance(response, dict) or not isinstance(response.get("requests"), list) or "clarify" not in response:
        return f"回應格式不符合合約：{json.dumps(response, ensure_ascii=False)[:120]}"
    if bool(response["clarify"]) != case["clarify"]:
        return f"clarify 應為 {case['clarify']}，實際 {response['clarify']}"
    if case["clarify"]:
        return None

    expected = sorted(case["expected"], key=_key)
    got = sorted(response["requests"], key=_key)
    if len(got) != len(expected):
        return f"應有 {len(expected)} 筆假單，實際 {len(got)} 筆"
    for i, (want, have) in enumerate(zip(expected, got), start=1):
        for name in FIELDS:
            if have.get(name) != want[name]:
                return f"第 {i} 筆 {name} 應為 {want[name]!r}，實際 {have.get(name)!r}"
    return None


def evaluate(cases: Iterable[dict], post: Post) -> Result:
    result = Result()
    for case in cases:
        result.total += 1
        try:
            reason = compare(case, post(case["sentence"], case["today"]))
        except Exception as exc:  # 一句失敗不該讓整份 eval 中斷
            reason = f"呼叫失敗：{exc}"
        if reason is None:
            result.passed += 1
        else:
            result.failures.append((case["id"], reason))
    return result


def http_post(base_url: str, timeout: float = 120) -> Post:
    url = base_url.rstrip("/") + "/api/parse"

    def post(sentence: str, today: str) -> dict:
        body = json.dumps({"sentence": sentence, "today": today}).encode("utf-8")
        request = urllib.request.Request(url, data=body, headers={"Content-Type": "application/json"})
        try:
            with urllib.request.urlopen(request, timeout=timeout) as response:
                return json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            raise RuntimeError(f"{url} 回傳 HTTP {exc.code}") from exc
        except (urllib.error.URLError, OSError) as exc:
            raise RuntimeError(f"連不上 {url}：backend 有沒有啟動？（{exc}）") from exc

    return post


def load_cases(path: Path, tags: set[str] | None) -> list[dict]:
    cases = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
    if tags:
        cases = [c for c in cases if tags & set(c.get("tags", []))]
    return cases


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="用 eval 集驗收 /api/parse")
    parser.add_argument("--url", default="http://localhost:8000", help="backend 位址")
    parser.add_argument("--fixtures", default=str(DEFAULT_FIXTURES))
    parser.add_argument("--tags", default="", help="逗號分隔，只跑帶這些標籤的句子")
    parser.add_argument("--min", type=float, default=None, help="準確率門檻（0–1），低於就 exit 1")
    args = parser.parse_args(argv)

    tags = {t.strip() for t in args.tags.split(",") if t.strip()} or None
    cases = load_cases(Path(args.fixtures), tags)
    result = evaluate(cases, http_post(args.url))

    for case_id, reason in result.failures:
        print(f"✗ {case_id}  {reason}")
    print(f"\n準確率 {result.passed}/{result.total} = {result.accuracy:.0%}")

    if args.min is not None and result.accuracy < args.min:
        print(f"低於門檻 {args.min:.0%}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
