"""請假業務規則：純函式，不碰資料庫與環境變數（SDS 模組接縫、ADR-01）。"""

import re
from dataclasses import dataclass, field
from datetime import date, timedelta

REASON_MAX_LENGTH = 200

LEAVE_TYPES = ("annual", "personal", "sick")
PERIODS = ("full_day", "am", "pm")
DATE_PATTERN = re.compile(r"\d{4}-\d{2}-\d{2}")

ALLOWED_FIELDS = ("employee_id", "leave_type", "start_date", "end_date", "period", "reason")
SERVER_FIELDS = {"status": "狀態不能由申請人指定", "days": "天數不能由申請人指定"}


@dataclass
class ValidationResult:
    errors: list[dict] = field(default_factory=list)
    leave: dict | None = None


def is_workday(day: date) -> bool:
    return day.weekday() < 5  # 週一至週五；國定假日不排除（Brief NG-03）


def count_leave_days(start: date, end: date, period: str) -> float:
    # 前提 end >= start；回傳 0 代表沒有工作日，由呼叫端轉成 no_workday。
    if period != "full_day":
        return 0.5 if is_workday(start) else 0
    span = (end - start).days + 1
    return sum(1 for offset in range(span) if is_workday(start + timedelta(days=offset)))


def normalize_reason(value) -> str:
    return "" if value is None else value.strip()


def error(field_name: str | None, code: str, message: str) -> dict:
    return {"field": field_name, "code": code, "message": message}


def check_date_range(start: date, end: date, period: str) -> dict | None:
    # API-03 驗證順序第 4 步：跨欄位規則最多產生一條。
    if end < start:
        return error("end_date", "end_before_start", "結束日期不能早於開始日期")
    if period != "full_day" and end != start:
        return error("period", "half_day_multi_day", "半天假只能選同一天")
    if count_leave_days(start, end, period) == 0:
        return error(None, "no_workday", "選擇的日期沒有工作日")
    return None


def check_keys(payload: dict) -> list[dict]:
    errors = []
    for key in payload:
        if key in SERVER_FIELDS:
            errors.append(error(key, "client_field_forbidden", SERVER_FIELDS[key]))
        elif key not in ALLOWED_FIELDS:
            errors.append(error(key, "unknown_field", f"不接受的欄位：{key}"))
    return errors


def check_choice(payload: dict, name: str, choices, required_message: str, invalid_message: str):
    value = payload.get(name)
    if value is None or value == "":
        return None, error(name, "required", required_message)
    if not isinstance(value, str) or value not in choices:
        return None, error(name, "invalid_value", invalid_message)
    return value, None


def check_employee(payload: dict, employee_ids: set[str]):
    value = payload.get("employee_id")
    if value is None or value == "":
        return None, error("employee_id", "required", "請選擇員工")
    if not isinstance(value, str):
        return None, error("employee_id", "invalid_value", "員工資料不正確")
    if value not in employee_ids:
        return None, error("employee_id", "employee_not_found", "找不到這位員工")
    return value, None


def check_date(payload: dict, name: str, label: str):
    value = payload.get(name)
    if value is None or value == "":
        return None, error(name, "required", f"請填寫{label}")
    if not isinstance(value, str):
        return None, error(name, "invalid_value", f"{label}格式不正確")
    if not DATE_PATTERN.fullmatch(value):
        return None, error(name, "invalid_date", f"{label}格式不正確")
    try:
        return date.fromisoformat(value), None
    except ValueError:
        return None, error(name, "invalid_date", f"{label}格式不正確")


def check_reason(payload: dict):
    value = payload.get("reason")
    if value is not None and not isinstance(value, str):
        return None, error("reason", "invalid_value", "理由格式不正確")
    reason = normalize_reason(value)
    if len(reason) > REASON_MAX_LENGTH:
        return None, error("reason", "reason_too_long", f"理由最多 {REASON_MAX_LENGTH} 字")
    return reason, None


def validate_leave_request(payload: dict, employee_ids: set[str]) -> ValidationResult:
    # 第 2 步：status、days 由伺服器決定，其他未定義的鍵一律拒絕。
    errors = check_keys(payload)

    # 第 3 步：逐欄檢查必填、型別與合法值。
    checks = [
        check_employee(payload, employee_ids),
        check_choice(payload, "leave_type", LEAVE_TYPES, "請選擇假別", "假別不正確"),
        check_date(payload, "start_date", "開始日期"),
        check_date(payload, "end_date", "結束日期"),
        check_choice(payload, "period", PERIODS, "請選擇時段", "時段不正確"),
        check_reason(payload),
    ]
    errors.extend(problem for _, problem in checks if problem)
    employee_id, leave_type, start, end, period, reason = (value for value, _ in checks)

    # 第 4 步：只有日期與時段各自合法時，才檢查跨欄位規則。
    if start and end and period:
        range_error = check_date_range(start, end, period)
        if range_error:
            errors.append(range_error)

    if errors:
        return ValidationResult(errors=errors)
    leave = {
        "employee_id": employee_id,
        "leave_type": leave_type,
        "start_date": payload["start_date"],
        "end_date": payload["end_date"],
        "period": period,
        "reason": reason,
        "days": count_leave_days(start, end, period),
        "status": "pending",
    }
    return ValidationResult(leave=leave)
