import openpyxl
import pandas as pd
import pytest

from unspsc_cards.reader import detect_header_row, read_codeset, records_from_frame

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


def real_frame() -> pd.DataFrame:
    """A one-row frame using the real column names, with numeric code cells (as the xlsx stores)."""
    return pd.DataFrame(
        {
            "Version": ["UNv260801"],
            "Key": [100004],
            "Segment": [10000000],
            "Segment Title": ["Live Plant and Animal Material"],
            "Segment Definition": ["This segment includes live..."],
            "Family": [10100000],
            "Family Title": ["Live animals"],
            "Family Definition": [None],
            "Class": [10101500],
            "Class Title": ["Livestock"],
            "Class Definition": [None],
            "Commodity": [10101501],
            "Commodity Title": ["Cats"],
            "Commodity Definition": [None],
            "Synonym": [None],
            "Acronym": [None],
        }
    )


def test_records_from_frame_normalizes_codes_to_strings():
    rec = next(iter(records_from_frame(real_frame())))
    assert rec.segment_code == "10000000"
    assert rec.family_code == "10100000"
    assert rec.class_code == "10101500"
    assert rec.commodity_code == "10101501"
    assert rec.commodity_title == "Cats"


def test_records_from_frame_blank_cells_become_none():
    rec = next(iter(records_from_frame(real_frame())))
    assert rec.commodity_definition is None
    assert rec.synonym is None
    assert rec.acronym is None
    assert rec.letter is None


def test_records_from_frame_keeps_present_definition():
    rec = next(iter(records_from_frame(real_frame())))
    assert rec.segment_definition == "This segment includes live..."


def test_records_from_frame_auto_detects_letter_column():
    df = real_frame()
    df["Letter"] = ["G"]
    rec = next(iter(records_from_frame(df)))
    assert rec.letter == "G"


def test_records_from_frame_works_without_definition_columns():
    df = real_frame().drop(
        columns=[
            "Segment Definition",
            "Family Definition",
            "Class Definition",
            "Commodity Definition",
        ]
    )
    rec = next(iter(records_from_frame(df)))
    assert rec.segment_definition is None
    assert rec.segment_title == "Live Plant and Animal Material"


def test_records_from_frame_missing_required_column_raises():
    df = real_frame().drop(columns=["Commodity"])
    with pytest.raises(ValueError):
        list(records_from_frame(df))


def test_records_from_frame_skips_blank_rows():
    df = pd.concat([real_frame(), real_frame()], ignore_index=True)
    df.loc[1, "Commodity"] = None  # blank leaf -> row skipped
    assert len(list(records_from_frame(df))) == 1


def test_detect_header_row_finds_label_row():
    raw = pd.DataFrame(
        [
            ["UNSPSC UNv260801", None, None, None, None],
            ["© 2023 UNDP", None, None, None, None],
            ["Version", "Segment", "Family", "Class", "Commodity"],
        ]
    )
    assert detect_header_row(raw) == 2


def test_detect_header_row_raises_when_absent():
    raw = pd.DataFrame([["nothing", "useful", "here"]])
    with pytest.raises(ValueError):
        detect_header_row(raw)


def _write_xlsx_like_real(path: str) -> None:
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.append(["UNSPSC UNv260801"])
    ws.append(["© 2023 United Nations Development Programme (UNDP)."])
    for _ in range(10):  # preamble padding so the header lands on row 13
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


def test_read_codeset_skips_preamble_and_reads_rows(tmp_path):
    path = tmp_path / "mini.xlsx"
    _write_xlsx_like_real(str(path))
    recs = list(read_codeset(path))
    assert len(recs) == 1
    assert recs[0].commodity_code == "10101501"
    assert recs[0].commodity_title == "Cats"
    assert recs[0].segment_definition == "seg def"
