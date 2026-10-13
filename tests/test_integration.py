from pathlib import Path
import subprocess
import sys

import pytest

from order_report import main, run_report
from order_reporting.config import ReportConfig
from order_reporting.file_io import read_orders
from order_reporting.validation import DataValidationError

ROOT = Path(__file__).resolve().parents[1]
REPORT_NAMES = ["overview.csv", "sales_by_category.csv", "sales_by_region.csv", "returns_by_category.csv"]


@pytest.mark.parametrize("filename", REPORT_NAMES)
def test_reports_match_original_content(tmp_path, filename):
    run_report(ReportConfig(ROOT / "data/orders.csv", tmp_path / "reports"))
    generated = (tmp_path / "reports" / filename).read_bytes().replace(b"\r\n", b"\n")
    baseline = (ROOT / "tests/baseline" / filename).read_bytes().replace(b"\r\n", b"\n")
    assert generated == baseline


def test_missing_file(tmp_path):
    with pytest.raises(FileNotFoundError, match="CSV-filen saknas"):
        read_orders(tmp_path / "missing.csv")


def test_empty_file(tmp_path):
    path = tmp_path / "empty.csv"
    path.write_text("", encoding="utf-8")
    with pytest.raises(DataValidationError, match="tom"):
        read_orders(path)


def test_header_only_file(tmp_path, orders):
    path = tmp_path / "headers.csv"
    orders.iloc[:0].to_csv(path, index=False)
    with pytest.raises(DataValidationError, match="inga orderrader"):
        run_report(ReportConfig(path, tmp_path / "reports"))
    assert not (tmp_path / "reports").exists()


def test_malformed_csv(tmp_path):
    path = tmp_path / "broken.csv"
    path.write_text('a,b\n"unclosed,2', encoding="utf-8")
    with pytest.raises(DataValidationError, match="felaktig struktur"):
        read_orders(path)


def test_main_returns_failure_and_logs(tmp_path, caplog):
    assert main(["--input", str(tmp_path / "missing.csv")]) == 1
    assert "CSV-filen saknas" in caplog.text


def test_output_path_is_a_file(tmp_path, caplog):
    path = tmp_path / "file"
    path.write_text("keep", encoding="utf-8")
    assert main(["--input", str(ROOT / "data/orders.csv"), "--output", str(path)]) == 1
    assert "Kunde inte skapa rapporterna" in caplog.text
    assert path.read_text(encoding="utf-8") == "keep"


def test_cli_from_another_directory(tmp_path):
    result = subprocess.run([
        sys.executable, str(ROOT / "order_report.py"),
        "--input", str(ROOT / "data/orders.csv"), "--output", str(tmp_path / "reports"),
    ], cwd=tmp_path, capture_output=True)
    assert result.returncode == 0, result.stderr
    assert sorted(p.name for p in (tmp_path / "reports").iterdir()) == sorted(REPORT_NAMES)


def test_import_has_no_side_effects():
    code = '''
import logging
from pathlib import Path
from unittest.mock import patch
before = list(logging.getLogger().handlers)
with patch("pandas.read_csv", side_effect=AssertionError("read on import")), \
     patch("pandas.DataFrame.to_csv", side_effect=AssertionError("write on import")), \
     patch.object(Path, "mkdir", side_effect=AssertionError("mkdir on import")):
    import order_report
assert list(logging.getLogger().handlers) == before
'''
    result = subprocess.run([sys.executable, "-c", code], cwd=ROOT, capture_output=True)
    assert result.returncode == 0, result.stderr
    assert result.stdout == b""
    assert result.stderr == b""
