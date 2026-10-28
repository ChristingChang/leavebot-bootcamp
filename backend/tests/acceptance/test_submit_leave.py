import sqlite3

import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.mark.req("TC-01", "AC-01.1", "FR-02", "FR-06", "FR-08", "FR-09", "NFR-03")
def test_tc01_submit_spanning_weekend_is_two_days_pending_and_persisted(client, valid_payload):
    response = client.post("/api/leaves", json=valid_payload)

    assert response.status_code == 201
    leave = response.json()["leave"]
    assert leave["days"] == 2
    assert leave["status"] == "pending"
    assert leave["reason"] == ""
    for field in ("employee_id", "leave_type", "start_date", "end_date", "period"):
        assert leave[field] == valid_payload[field]

    listed = client.get("/api/employees/E001/leaves")
    assert listed.status_code == 200
    assert listed.json() == {"leaves": [leave]}

    # 同一個 LEAVEBOT_DB 檔案、新的 client，資料仍在。
    with TestClient(app) as fresh_client:
        reread = fresh_client.get("/api/employees/E001/leaves")
    assert reread.json() == {"leaves": [leave]}


@pytest.mark.req("TC-09", "FR-01")
def test_tc09_employees_listed_in_id_order(client):
    response = client.get("/api/employees")

    assert response.status_code == 200
    assert response.json() == {
        "employees": [
            {"id": "E001", "name": "王小明"},
            {"id": "E002", "name": "李小華"},
            {"id": "E003", "name": "陳小美"},
        ]
    }


@pytest.mark.req("TC-09", "AC-03.1", "FR-09")
def test_tc09_each_employee_sees_only_own_leaves(client, valid_payload):
    assert client.post("/api/leaves", json=valid_payload).status_code == 201
    assert client.post("/api/leaves", json={**valid_payload, "employee_id": "E002"}).status_code == 201

    e001 = client.get("/api/employees/E001/leaves").json()["leaves"]
    e002 = client.get("/api/employees/E002/leaves").json()["leaves"]
    assert [leave["employee_id"] for leave in e001] == ["E001"]
    assert [leave["employee_id"] for leave in e002] == ["E002"]
    assert client.get("/api/employees/E003/leaves").json() == {"leaves": []}


@pytest.mark.req("TC-09", "FR-01", "FR-09")
def test_tc09_unknown_employee_leaves_is_404(client):
    response = client.get("/api/employees/E999/leaves")

    assert response.status_code == 404
    assert {"field": "employee_id", "code": "employee_not_found"} in [
        {"field": e["field"], "code": e["code"]} for e in response.json()["errors"]
    ]


def leave_count(client, employee_id="E001"):
    return len(client.get(f"/api/employees/{employee_id}/leaves").json()["leaves"])


def error_pairs(response):
    return {(error["field"], error["code"]) for error in response.json()["errors"]}


@pytest.mark.req("TC-04", "AC-02.2", "FR-04")
def test_tc04_end_before_start_is_rejected(client, valid_payload):
    valid_payload.update(start_date="2026-10-20", end_date="2026-10-19", period="full_day")

    response = client.post("/api/leaves", json=valid_payload)

    assert response.status_code == 422
    assert ("end_date", "end_before_start") in error_pairs(response)
    assert leave_count(client) == 0


@pytest.mark.req("TC-02", "AC-01.2", "AC-01.3", "FR-09")
def test_tc02_half_day_and_past_date_listed_newest_first(client, valid_payload):
    half_day = {
        **valid_payload,
        "leave_type": "personal",
        "start_date": "2026-10-13",
        "end_date": "2026-10-13",
        "period": "am",
    }
    past_date = {
        **valid_payload,
        "leave_type": "sick",
        "start_date": "2026-10-05",
        "end_date": "2026-10-05",
        "period": "full_day",
    }

    a = client.post("/api/leaves", json=half_day)
    assert a.status_code == 201
    assert a.json()["leave"]["days"] == 0.5
    assert a.json()["leave"]["status"] == "pending"

    b = client.post("/api/leaves", json=past_date)
    assert b.status_code == 201
    assert b.json()["leave"]["days"] == 1
    assert b.json()["leave"]["status"] == "pending"

    listed = client.get("/api/employees/E001/leaves").json()["leaves"]
    assert [leave["id"] for leave in listed] == [b.json()["leave"]["id"], a.json()["leave"]["id"]]


@pytest.mark.req("TC-05", "AC-02.3", "FR-05")
def test_tc05_half_day_across_days_is_rejected(client, valid_payload):
    valid_payload.update(start_date="2026-10-13", end_date="2026-10-14", period="pm")

    response = client.post("/api/leaves", json=valid_payload)

    assert response.status_code == 422
    assert ("period", "half_day_multi_day") in error_pairs(response)
    assert leave_count(client) == 0


@pytest.mark.req("TC-06", "AC-02.4", "FR-06")
@pytest.mark.parametrize(
    ("start_date", "end_date", "period"),
    [
        ("2026-10-17", "2026-10-18", "full_day"),
        ("2026-10-17", "2026-10-17", "am"),
    ],
    ids=["a-weekend-full-day", "b-saturday-am"],
)
def test_tc06_weekend_only_is_rejected(client, valid_payload, start_date, end_date, period):
    valid_payload.update(start_date=start_date, end_date=end_date, period=period)

    response = client.post("/api/leaves", json=valid_payload)

    assert response.status_code == 422
    assert (None, "no_workday") in error_pairs(response)
    assert leave_count(client) == 0


@pytest.mark.req("TC-11", "NFR-01", "NFR-04")
def test_tc11_database_failure_returns_500_and_saves_nothing(client, valid_payload, monkeypatch):
    from app import db

    detail = "disk I/O error near INSERT INTO leave_requests"

    def broken_insert(conn, leave):
        raise sqlite3.OperationalError(detail)

    # 只在 POST 期間替換 insert_leave；不可用 monkeypatch.undo()，它會連 conftest 的 LEAVEBOT_DB 一起還原。
    with monkeypatch.context() as m:
        m.setattr(db, "insert_leave", broken_insert)
        response = client.post("/api/leaves", json=valid_payload)

    assert response.status_code == 500
    errors = response.json()["errors"]
    assert {"field": None, "code": "database_error"} in [
        {"field": e["field"], "code": e["code"]} for e in errors
    ]
    for error in errors:
        assert "disk I/O" not in error["message"]
        assert "INSERT" not in error["message"]

    assert db.insert_leave is not broken_insert
    assert client.get("/api/employees/E001/leaves").json() == {"leaves": []}


@pytest.mark.req("TC-03", "AC-02.1", "FR-01", "FR-03")
@pytest.mark.parametrize(
    ("changes", "removed", "expected_errors"),
    [
        ({}, "leave_type", {("leave_type", "required")}),
        ({"leave_type": "Annual"}, None, {("leave_type", "invalid_value")}),
        ({"employee_id": "E999"}, None, {("employee_id", "employee_not_found")}),
        ({"start_date": "2026-02-30"}, None, {("start_date", "invalid_date")}),
        (
            {"start_date": "2026-10-20", "end_date": "2026-10-19"},
            "leave_type",
            {("leave_type", "required"), ("end_date", "end_before_start")},
        ),
    ],
    ids=[
        "a-missing-leave-type",
        "b-leave-type-wrong-case",
        "c-unknown-employee",
        "d-nonexistent-date",
        "e-multiple-errors",
    ],
)
def test_tc03_invalid_fields_are_rejected(client, valid_payload, changes, removed, expected_errors):
    valid_payload.update(changes)
    if removed:
        del valid_payload[removed]

    response = client.post("/api/leaves", json=valid_payload)

    assert response.status_code == 422
    assert expected_errors <= error_pairs(response)
    assert leave_count(client) == 0


@pytest.mark.req("TC-08", "FR-08", "FR-03")
@pytest.mark.parametrize(
    ("extra", "expected_error"),
    [
        ({"status": "approved"}, ("status", "client_field_forbidden")),
        ({"days": 2}, ("days", "client_field_forbidden")),
        ({"foo": "x"}, ("foo", "unknown_field")),
    ],
    ids=["a-status", "b-days-same-as-computed", "c-unknown-field"],
)
def test_tc08_client_cannot_send_extra_fields(client, valid_payload, extra, expected_error):
    valid_payload.update(extra)

    response = client.post("/api/leaves", json=valid_payload)

    assert response.status_code == 422
    assert expected_error in error_pairs(response)
    assert leave_count(client) == 0


@pytest.mark.req("TC-10", "AC-02.5", "FR-07")
def test_tc10_reason_over_limit_is_not_saved(client, valid_payload):
    valid_payload["reason"] = "a" * 201

    response = client.post("/api/leaves", json=valid_payload)

    assert response.status_code == 422
    assert leave_count(client) == 0


@pytest.mark.req("TC-10", "FR-07", "NFR-02")
def test_tc10_sql_fragment_reason_is_stored_verbatim(client, valid_payload):
    valid_payload["reason"] = "'); DROP TABLE x;--"

    response = client.post("/api/leaves", json=valid_payload)

    assert response.status_code == 201
    listed = client.get("/api/employees/E001/leaves")
    assert listed.status_code == 200
    assert [leave["reason"] for leave in listed.json()["leaves"]] == ["'); DROP TABLE x;--"]
    assert client.get("/api/employees/E001/leaves").status_code == 200


@pytest.mark.req("TC-03", "SDS API-03")
@pytest.mark.parametrize(
    "body",
    [
        pytest.param("not json", id="f1-raw-text"),
        pytest.param("[]", id="f2-json-array"),
    ],
)
def test_tc03_f_non_object_body_is_400(client, body):
    response = client.post(
        "/api/leaves", content=body, headers={"Content-Type": "application/json"}
    )

    assert response.status_code == 400
    assert {"field": None, "code": "invalid_body"} in [
        {"field": e["field"], "code": e["code"]} for e in response.json()["errors"]
    ]
    assert client.get("/api/employees/E001/leaves").json() == {"leaves": []}
