import openpyxl
from typer.testing import CliRunner

from unspsc_cards.cli import app

runner = CliRunner()

COLUMNS = [
    "Version",
    "Key",
    "Segment",
    "Segment Title",
    "Segment Definition",
    "Family",
    "Family Title",
    "Family Definition",
    "Class",
    "Class Title",
    "Class Definition",
    "Commodity",
    "Commodity Title",
    "Commodity Definition",
    "Synonym",
    "Acronym",
]


def _write_xlsx(path: str) -> None:
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.append(["UNSPSC UNv260801"])
    ws.append(["© 2023 United Nations Development Programme (UNDP)."])
    for _ in range(10):
        ws.append([None])
    ws.append(COLUMNS)
    ws.append(
        [
            "UNv260801",
            100004,
            10000000,
            "Live Plant and Animal Material",
            "seg def",
            10100000,
            "Live animals",
            None,
            10101500,
            "Livestock",
            None,
            10101501,
            "Cats",
            None,
            None,
            None,
        ]
    )
    wb.save(path)


def test_cli_build_generates_site(tmp_path):
    xlsx = tmp_path / "mini.xlsx"
    _write_xlsx(str(xlsx))
    out = tmp_path / "site"

    result = runner.invoke(app, ["build", str(xlsx), "--out", str(out)])

    assert result.exit_code == 0, result.output
    assert (out / "index.html").is_file()
    assert (out / "a-z" / "index.html").is_file()  # A–Z concordance landing
    commodity = out / "10" / "10" / "15" / "10101501.html"  # named file in its class dir
    assert commodity.is_file()
    assert "Cats" in commodity.read_text(encoding="utf-8")


def test_cli_build_missing_input_errors(tmp_path):
    result = runner.invoke(app, ["build", str(tmp_path / "nope.xlsx"), "--out", str(tmp_path)])
    assert result.exit_code != 0
