"""Read a UNSPSC xlsx export into ``Record`` objects.

The export has a multi-row title/copyright preamble, so the header row is located by content
(the row carrying Segment/Family/Class/Commodity) rather than assumed to be row 1. Column names
are matched case-insensitively, and a letter/grouping column is used only if one is present.
"""

from __future__ import annotations

import math
from collections.abc import Iterator
from pathlib import Path

import pandas as pd

from .codes import normalize_code
from .model import Record

CODE_COLUMNS = {
    "segment_code": "Segment",
    "family_code": "Family",
    "class_code": "Class",
    "commodity_code": "Commodity",
}
TITLE_COLUMNS = {
    "segment_title": "Segment Title",
    "family_title": "Family Title",
    "class_title": "Class Title",
    "commodity_title": "Commodity Title",
}
DEFINITION_COLUMNS = {
    "segment_definition": "Segment Definition",
    "family_definition": "Family Definition",
    "class_definition": "Class Definition",
    "commodity_definition": "Commodity Definition",
}
EXTRA_COLUMNS = {"synonym": "Synonym", "acronym": "Acronym"}

REQUIRED_COLUMNS = {**CODE_COLUMNS, **TITLE_COLUMNS}
OPTIONAL_COLUMNS = {**DEFINITION_COLUMNS, **EXTRA_COLUMNS}

_LEVEL_HEADERS = {"segment", "family", "class", "commodity"}
_PREAMBLE_SCAN_ROWS = 40


def detect_header_row(raw: pd.DataFrame) -> int:
    """Return the 0-based index of the row that holds the column headers.

    The header is the first row whose cells include all four level labels.
    """
    for i in range(len(raw)):
        values = {str(v).strip().lower() for v in raw.iloc[i].tolist()}
        if values >= _LEVEL_HEADERS:
            return i
    raise ValueError("could not locate the header row (Segment/Family/Class/Commodity)")


def _detect_letter_column(columns: list[object]) -> object | None:
    """Return the column label of a letter/grouping column if one is present, else None."""
    for col in columns:
        if "letter" in str(col).strip().lower():
            return col
    return None


def _clean(value: object) -> str | None:
    """Strip text; turn None/NaN/empty into None."""
    if value is None:
        return None
    if isinstance(value, float) and math.isnan(value):
        return None
    text = str(value).strip()
    return text or None


def _is_blank(value: object) -> bool:
    if value is None:
        return True
    if isinstance(value, float) and math.isnan(value):
        return True
    return str(value).strip() == ""


def records_from_frame(df: pd.DataFrame) -> Iterator[Record]:
    """Yield a ``Record`` per data row, normalizing codes and cleaning text.

    Raises ValueError if a required column (a level code or title) is absent. Rows whose
    Commodity code is blank are skipped (structural blank rows).
    """
    columns = list(df.columns)
    lookup = {str(c).strip().lower(): c for c in columns}

    field_to_col: dict[str, object] = {}
    for field, label in REQUIRED_COLUMNS.items():
        col = lookup.get(label.lower())
        if col is None:
            raise ValueError(f"missing required column: {label!r}")
        field_to_col[field] = col
    for field, label in OPTIONAL_COLUMNS.items():
        col = lookup.get(label.lower())
        if col is not None:
            field_to_col[field] = col

    letter_col = _detect_letter_column(columns)

    selected = list(field_to_col.values()) + ([letter_col] if letter_col is not None else [])
    inverse = {col: field for field, col in field_to_col.items()}
    if letter_col is not None:
        inverse[letter_col] = "letter"
    sub = df[selected].rename(columns=inverse)

    for row in sub.itertuples(index=False):
        data = row._asdict()
        if _is_blank(data["commodity_code"]):
            continue
        yield Record(
            segment_code=normalize_code(data["segment_code"]),
            segment_title=_clean(data["segment_title"]) or "",
            segment_definition=_clean(data.get("segment_definition")),
            family_code=normalize_code(data["family_code"]),
            family_title=_clean(data["family_title"]) or "",
            family_definition=_clean(data.get("family_definition")),
            class_code=normalize_code(data["class_code"]),
            class_title=_clean(data["class_title"]) or "",
            class_definition=_clean(data.get("class_definition")),
            commodity_code=normalize_code(data["commodity_code"]),
            commodity_title=_clean(data["commodity_title"]) or "",
            commodity_definition=_clean(data.get("commodity_definition")),
            letter=_clean(data.get("letter")),
            synonym=_clean(data.get("synonym")),
            acronym=_clean(data.get("acronym")),
        )


def read_codeset(path: str | Path) -> Iterator[Record]:
    """Read the xlsx at ``path`` and yield ``Record`` objects (header row auto-detected)."""
    raw = pd.read_excel(path, header=None, nrows=_PREAMBLE_SCAN_ROWS, dtype=object)
    header_row = detect_header_row(raw)
    df = pd.read_excel(path, header=header_row, dtype=object)
    yield from records_from_frame(df)
