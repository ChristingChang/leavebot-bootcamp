"""trace.py 的規格：規格文件的編號 → 測試計畫的 TC → 測試程式的 req 標註，三段要接得起來。"""

from pathlib import Path

from scripts.trace import build_report, main


def _write(root: Path, rel: str, text: str) -> None:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _project(tmp_path: Path, test_code: str = "") -> tuple[Path, Path]:
    docs, tests = tmp_path / "docs", tmp_path / "tests"
    _write(tmp_path, "docs/02-prd.md", "## US-01 送出請假\n\n- **AC-01.1** Given 一句話 When 送出 Then 看到預覽\n- **AC-01.2** Given 解析失敗 When 送出 Then 看到錯誤\n")
    _write(tmp_path, "docs/03-srs.md", "| 編號 | 需求 | 來源 |\n|---|---|---|\n| FR-01 | 解析一句話 | US-01 |\n| NFR-01 | 注入句不得改變假單狀態 | G-01 |\n")
    _write(tmp_path, "docs/06-test-plan.md", "## 測試案例\n\n| TC | 驗什麼 |\n|---|---|\n| TC-01 | AC-01.1、FR-01 |\n| TC-02 | AC-01.2 |\n\n## 不測什麼\n\n- NFR-01：本版只示範\n")
    _write(tmp_path, "tests/test_x.py", test_code)
    return docs, tests


def test_collects_defined_ids_from_headings_bold_and_table_first_cells(tmp_path):
    docs, tests = _project(tmp_path)

    report = build_report(docs, tests)

    assert {"AC-01.1", "AC-01.2", "FR-01", "NFR-01", "US-01", "TC-01", "TC-02"} <= report.defined


def test_a_mention_in_a_later_column_is_not_a_definition(tmp_path):
    docs, tests = _project(tmp_path)

    report = build_report(docs, tests)

    assert "G-01" not in report.defined


def test_tc_covers_the_ids_on_its_row(tmp_path):
    docs, tests = _project(tmp_path)

    report = build_report(docs, tests)

    assert report.tc_covers["TC-01"] == {"AC-01.1", "FR-01"}


def test_requirement_without_tc_is_a_gap(tmp_path):
    docs, tests = _project(tmp_path)
    _write(tmp_path, "docs/03-srs.md", "| FR-01 | 解析 | US-01 |\n| FR-02 | 存檔 | US-01 |\n")

    report = build_report(docs, tests)

    assert "FR-02" in report.untested_requirements
    assert "FR-01" not in report.untested_requirements


def test_ids_listed_under_not_tested_section_are_exempt(tmp_path):
    docs, tests = _project(tmp_path)

    report = build_report(docs, tests)

    assert "NFR-01" in report.exempt
    assert "NFR-01" not in report.untested_requirements


def test_tc_without_test_code_is_a_gap(tmp_path):
    docs, tests = _project(tmp_path, '@pytest.mark.req("TC-01", "AC-01.1")\ndef test_a(): ...\n')

    report = build_report(docs, tests)

    assert report.tc_without_tests == ["TC-02"]
    assert report.tests_by_id["TC-01"] == ["tests/test_x.py::test_a"]


def test_marker_pointing_at_unknown_id_is_reported(tmp_path):
    docs, tests = _project(tmp_path, "@pytest.mark.req('TC-09')\ndef test_b(): ...\n")

    report = build_report(docs, tests)

    assert report.unknown_refs == [("tests/test_x.py::test_b", "TC-09")]


def test_missing_tests_dir_means_nothing_is_tested_yet(tmp_path):
    docs, _ = _project(tmp_path)

    report = build_report(docs, tmp_path / "nope")

    assert report.tc_without_tests == ["TC-01", "TC-02"]


def test_strict_exits_1_when_there_are_gaps(tmp_path, capsys):
    docs, tests = _project(tmp_path)

    assert main(["--docs", str(docs), "--tests", str(tests)]) == 0
    assert main(["--docs", str(docs), "--tests", str(tests), "--strict"]) == 1
    assert "TC-02" in capsys.readouterr().out


def test_strict_passes_when_everything_is_connected(tmp_path):
    code = (
        '@pytest.mark.req("TC-01")\ndef test_a(): ...\n\n'
        '@pytest.mark.req("TC-02")\ndef test_b(): ...\n'
    )
    docs, tests = _project(tmp_path, code)

    assert main(["--docs", str(docs), "--tests", str(tests), "--strict"]) == 0
