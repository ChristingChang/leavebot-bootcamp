from datetime import date

import pytest

from app import leave_rules


@pytest.mark.req("TC-07", "FR-06")
@pytest.mark.parametrize(
    ("start", "end", "period", "expected"),
    [
        (date(2026, 10, 16), date(2026, 10, 19), "full_day", 2),
        (date(2026, 10, 12), date(2026, 10, 25), "full_day", 10),
        (date(2026, 10, 13), date(2026, 10, 13), "full_day", 1),
        (date(2026, 10, 13), date(2026, 10, 13), "am", 0.5),
        (date(2026, 10, 17), date(2026, 10, 18), "full_day", 0),
        (date(2026, 10, 17), date(2026, 10, 17), "pm", 0),
    ],
    ids=[
        "fri-to-mon-skips-weekend",
        "two-weeks-two-weekends",
        "same-day-full",
        "same-day-am",
        "weekend-only-full",
        "saturday-pm",
    ],
)
def test_tc07_count_leave_days_boundaries(start, end, period, expected):
    assert leave_rules.count_leave_days(start, end, period) == expected


EMPLOYEE_IDS = {"E001", "E002", "E003"}


@pytest.mark.req("TC-10", "AC-02.5", "FR-07")
@pytest.mark.parametrize(
    ("reason", "stored_reason"),
    [
        ("a" * 200, "a" * 200),
        ("假" * 200, "假" * 200),
        ("  " + "a" * 200 + "　　", "a" * 200),
        ("　　　", ""),
    ],
    ids=["200-ascii", "200-chinese", "edge-whitespace-not-counted", "only-fullwidth-spaces"],
)
def test_tc10_reason_within_limit_is_accepted(valid_payload, reason, stored_reason):
    valid_payload["reason"] = reason

    result = leave_rules.validate_leave_request(valid_payload, EMPLOYEE_IDS)

    assert result.errors == []
    assert result.leave["reason"] == stored_reason


@pytest.mark.req("TC-10", "AC-02.5", "FR-07")
@pytest.mark.parametrize("reason", ["a" * 201, "假" * 201], ids=["201-ascii", "201-chinese"])
def test_tc10_reason_over_limit_is_rejected(valid_payload, reason):
    valid_payload["reason"] = reason

    result = leave_rules.validate_leave_request(valid_payload, EMPLOYEE_IDS)

    assert ("reason", "reason_too_long") in {(e["field"], e["code"]) for e in result.errors}
    assert result.leave is None
