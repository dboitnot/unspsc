"""Pure utilities for UNSPSC codes: normalization, display, hierarchy, links.

A UNSPSC code is an 8-digit string: Segment(2) + Family(2) + Class(2) + Commodity(2).
Codes are always handled as zero-padded 8-character strings, never as integers.
"""

from __future__ import annotations

import math


def normalize_code(value: object) -> str:
    """Coerce an int/float/str cell value to a zero-padded 8-character code string.

    Handles the float artifacts pandas produces for numeric columns (e.g. ``10000000.0``)
    and rejects missing/non-numeric values.
    """
    if value is None:
        raise ValueError("UNSPSC code is missing (None)")
    if isinstance(value, float):
        if math.isnan(value):
            raise ValueError("UNSPSC code is missing (NaN)")
        value = int(value)
    if isinstance(value, int):
        text = str(value)
    else:
        text = str(value).strip()
        if text.endswith(".0"):
            text = text[:-2]
    if not text.isdigit():
        raise ValueError(f"invalid UNSPSC code: {value!r}")
    return text.zfill(8)


def display_code(code: str, letter: str | None = None) -> str:
    """Format an 8-char code for display: ``4411.1810`` or ``G-4411.1810`` with a letter."""
    body = f"{code[0:4]}.{code[4:8]}"
    return f"{letter}-{body}" if letter else body


def ancestor_code(code: str, level: int) -> str:
    """Return ``code`` with all groups below ``level`` zeroed.

    Levels: 1=Segment, 2=Family, 3=Class, 4=Commodity. ``ancestor_code('44111810', 2)``
    -> ``'44110000'`` (the Family). Level 4 returns the code unchanged.
    """
    keep = level * 2
    return code[:keep] + "0" * (8 - keep)


def group_at_level(code: str, level: int) -> str:
    """Return the 2-digit group occupying ``level``'s position (the dir name at that level)."""
    start = (level - 1) * 2
    return code[start : start + 2]


def path_parts(code: str, level: int) -> list[str]:
    """Return the per-level directory parts for a node, e.g. ('44111810', 4) -> [44,11,18,10]."""
    return [code[i : i + 2] for i in range(0, level * 2, 2)]


def child_href(child_code: str, child_level: int, is_leaf: bool) -> str:
    """Relative drill-down link to a child.

    A leaf child is a ``{code}.html`` file in the current directory; a branch child is its own
    ``{group}/index.html`` directory.
    """
    if is_leaf:
        return f"{child_code}.html"
    return f"{group_at_level(child_code, child_level)}/index.html"


def dir_depth(level: int, is_leaf: bool) -> int:
    """How many directories deep a node's file sits — a leaf lives in its parent's directory."""
    return level - 1 if is_leaf else level


def output_path(code: str, level: int, is_leaf: bool) -> tuple[list[str], str]:
    """Return the (directory parts, filename) for a node's HTML file under the site root.

    Branch nodes are written as ``{groups...}/index.html``; leaves as ``{code}.html`` in their
    parent's directory (e.g. commodity ``57050205`` -> ``57/05/02/57050205.html``).
    """
    if is_leaf:
        return path_parts(code, level - 1), f"{code}.html"
    return path_parts(code, level), "index.html"


def node_relpath(code: str, level: int, is_leaf: bool) -> str:
    """The node's HTML file path relative to the site root, e.g. ``57/05/02/57050205.html``."""
    dir_parts, filename = output_path(code, level, is_leaf)
    return "/".join([*dir_parts, filename])


def up_href(levels_up: int) -> str:
    """Relative up-navigation link climbing ``levels_up`` directories to an index.html."""
    return "../" * levels_up + "index.html"
