"""run_eval.py 的規格：把 fixtures 逐句打 /api/parse，逐欄比對，算準確率。"""

import json
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

import pytest

from scripts.run_eval import compare, evaluate, http_post, main

CASE = {
    "id": "L001", "today": "2026-10-12", "sentence": "明天請特休",
    "expected": [{"start_date": "2026-10-13", "end_date": "2026-10-13", "period": "full", "leave_type": "annual", "days": 1}],
    "clarify": False, "tags": ["basic"],
}
CLARIFY = {"id": "L030", "today": "2026-10-12", "sentence": "我想請假", "expected": [], "clarify": True, "tags": ["clarify"]}


def _fixture(tmp_path: Path, *cases) -> Path:
    path = tmp_path / "f.jsonl"
    path.write_text("\n".join(json.dumps(c, ensure_ascii=False) for c in cases) + "\n", encoding="utf-8")
    return path


def test_exact_match_passes():
    assert compare(CASE, {"requests": CASE["expected"], "clarify": False}) is None


def test_extra_fields_in_response_are_ignored():
    got = [dict(CASE["expected"][0], reason="看牙醫")]

    assert compare(CASE, {"requests": got, "clarify": False}) is None


def test_request_order_does_not_matter():
    two = dict(CASE, expected=[
        {"start_date": "2026-10-14", "end_date": "2026-10-14", "period": "pm", "leave_type": None, "days": 0.5},
        {"start_date": "2026-10-13", "end_date": "2026-10-13", "period": "full", "leave_type": "annual", "days": 1},
    ])

    assert compare(two, {"requests": list(reversed(two["expected"])), "clarify": False}) is None


def test_wrong_field_names_the_field():
    wrong = [dict(CASE["expected"][0], period="am")]

    assert "period" in compare(CASE, {"requests": wrong, "clarify": False})


def test_clarify_mismatch_fails():
    assert "clarify" in compare(CLARIFY, {"requests": CASE["expected"], "clarify": False})


def test_malformed_response_fails_with_reason():
    assert "格式" in compare(CASE, {"oops": 1})


def test_evaluate_counts_accuracy_and_survives_errors():
    def post(sentence, today):
        if sentence == "我想請假":
            raise RuntimeError("500")
        return {"requests": CASE["expected"], "clarify": False}

    result = evaluate([CASE, CLARIFY], post)

    assert result.passed == 1 and result.total == 2
    assert result.accuracy == 0.5
    assert "500" in result.failures[0][1]


def test_main_threshold_and_tag_filter(tmp_path, monkeypatch, capsys):
    fixture = _fixture(tmp_path, CASE, CLARIFY)
    monkeypatch.setattr("scripts.run_eval.http_post", lambda url: lambda s, t: {"requests": CASE["expected"], "clarify": False})

    assert main(["--fixtures", str(fixture)]) == 0
    assert main(["--fixtures", str(fixture), "--min", "0.9"]) == 1
    assert main(["--fixtures", str(fixture), "--tags", "basic", "--min", "0.9"]) == 0
    assert "L030" in capsys.readouterr().out


class _Handler(BaseHTTPRequestHandler):
    def do_POST(self):
        body = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
        payload = json.dumps({"requests": [], "clarify": body["sentence"] == "我想請假"}).encode()
        self.send_response(200 if self.path == "/api/parse" else 404)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(payload)

    def log_message(self, *args):
        pass


@pytest.fixture
def server():
    httpd = HTTPServer(("127.0.0.1", 0), _Handler)
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    yield f"http://127.0.0.1:{httpd.server_port}"
    httpd.shutdown()


def test_http_post_talks_to_the_parse_contract(server):
    post = http_post(server)

    assert post("我想請假", "2026-10-12") == {"requests": [], "clarify": True}


def test_http_post_unreachable_server_raises_readable_error():
    post = http_post("http://127.0.0.1:9")

    with pytest.raises(RuntimeError, match="連不上"):
        post("x", "2026-10-12")
