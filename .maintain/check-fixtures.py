"""eval 起始集的格式檢查。不檢查 AI，只確保「標準答案」本身沒有寫錯。

只用標準函式庫：上課 repo 沒有 pyproject，維護者不用先建 venv。
無輸出 = 沒問題；有問題時逐條列出並 exit 1。
"""

import json
import sys
from datetime import date, timedelta
from pathlib import Path

FIXTURE = Path(__file__).resolve().parents[1] / "course" / "fixtures" / "leave-sentences.jsonl"
PERIODS = {"full", "am", "pm"}
LEAVE_TYPES = {"annual", "personal", "sick", "menstrual", "marriage", "bereavement", None}
REQUIRED = {"id", "today", "sentence", "expected", "clarify", "tags"}


def workdays(start: date, end: date) -> int:
    return sum(1 for i in range((end - start).days + 1) if (start + timedelta(i)).weekday() < 5)


def check_request(case: dict, req: dict) -> list[str]:
    today = date.fromisoformat(case["today"])
    start = date.fromisoformat(req["start_date"])
    end = date.fromisoformat(req["end_date"])
    problems = []
    if start > end:
        problems.append("起日晚於訖日")
    if req["period"] not in PERIODS:
        problems.append(f"period 不合法：{req['period']}")
    if req["leave_type"] not in LEAVE_TYPES:
        problems.append(f"leave_type 不合法：{req['leave_type']}")
    if start.weekday() >= 5 or end.weekday() >= 5:
        problems.append("起訖日落在週末")
    if req["period"] == "full" and req["days"] != workdays(start, end):
        problems.append(f"天數應為 {workdays(start, end)}，寫成 {req['days']}")
    if req["period"] != "full" and (start != end or req["days"] != 0.5):
        problems.append("半天假應該是同一天、0.5 天")
    if "past" not in case["tags"] and start < today:
        problems.append("日期早於今天，卻沒有標 past")
    return problems


def check_case(case: dict) -> list[str]:
    missing = REQUIRED - set(case)
    if missing:
        return [f"缺欄位 {sorted(missing)}"]
    problems = []
    if not case["sentence"].strip():
        problems.append("句子是空的")
    if not isinstance(case["tags"], list):
        problems.append("tags 不是 list")
    if case["clarify"] and case["expected"]:
        problems.append("要追問的句子不該有預期假單")
    if not case["clarify"] and not case["expected"]:
        problems.append("不追問的句子至少要有一筆預期假單")
    for req in case["expected"]:
        problems.extend(check_request(case, req))
    return problems


def main() -> int:
    lines = [line for line in FIXTURE.read_text(encoding="utf-8").splitlines() if line.strip()]
    problems = []
    cases = []
    for number, line in enumerate(lines, start=1):
        try:
            cases.append(json.loads(line))
        except json.JSONDecodeError as error:
            problems.append(f"第 {number} 行不是合法 JSON：{error}")
    if len(cases) < 30:
        problems.append(f"至少要 30 句，現在 {len(cases)} 句")
    ids = [case.get("id") for case in cases]
    duplicates = sorted({i for i in ids if ids.count(i) > 1})
    if duplicates:
        problems.append(f"id 重複：{duplicates}")
    for case in cases:
        problems.extend(f"{case.get('id', '?')}：{p}" for p in check_case(case))
    for problem in problems:
        print(problem)
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
