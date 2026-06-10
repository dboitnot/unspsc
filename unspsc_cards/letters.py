"""UNGM A–J letter categories that group the UNSPSC segments (used on the index page only).

These categories are a curated *semantic* grouping, not numeric ranges: e.g. category D mixes
segments 22, 25, 40 and 95, and category B omits 22/25 (which sit in D). Membership is therefore
defined explicitly. Segments not covered by any category fall into a trailing "Other" group so
the index never silently drops a segment.
"""

from __future__ import annotations

from dataclasses import dataclass

from .model import Node

# (letter, name, segment codes) in canonical A–J order; codes are in canonical order within a group.
LETTER_GROUPS: list[tuple[str, str, list[str]]] = [
    (
        "A",
        "Raw Materials, Chemicals, Paper, Fuel",
        ["10000000", "11000000", "12000000", "13000000", "14000000", "15000000"],
    ),
    (
        "B",
        "Industrial Equipment & Tools",
        ["20000000", "21000000", "23000000", "24000000", "26000000", "27000000"],
    ),
    (
        "C",
        "Components & Supplies",
        ["30000000", "31000000", "32000000", "39000000"],
    ),
    (
        "D",
        "Construction, Transportation & Facility Equipment & Supplies",
        ["22000000", "25000000", "40000000", "95000000"],
    ),
    (
        "E",
        "Medical, Laboratory & Test Equipment & Supplies & Pharmaceuticals",
        ["41000000", "42000000", "51000000"],
    ),
    (
        "F",
        "Food, Cleaning & Service Industry Equipment & Supplies",
        ["47000000", "48000000", "50000000"],
    ),
    (
        "G",
        "Business, Communication & Technology Equipment & Supplies",
        ["43000000", "44000000", "45000000", "55000000"],
    ),
    (
        "H",
        "Defense, Security & Safety Equipment & Supplies",
        ["46000000", "57000000"],
    ),
    (
        "I",
        "Personal, Domestic & Consumer Equipment & Supplies",
        ["49000000", "52000000", "53000000", "54000000", "56000000", "60000000"],
    ),
    (
        "J",
        "Services",
        [
            "64000000",
            "70000000",
            "71000000",
            "72000000",
            "73000000",
            "76000000",
            "77000000",
            "78000000",
            "80000000",
            "81000000",
            "82000000",
            "83000000",
            "84000000",
            "85000000",
            "86000000",
            "90000000",
            "91000000",
            "92000000",
            "93000000",
            "94000000",
        ],
    ),
]


@dataclass
class LetterGroup:
    """A category heading plus the segment nodes that belong to it (in canonical order)."""

    letter: str
    name: str
    anchor: str
    segments: list[Node]


def grouped_segments(root: Node) -> list[LetterGroup]:
    """Group the root's segment children under the A–J categories, in A–J order.

    Empty categories are skipped. Any segment not listed in a category is collected into a
    trailing "Other" group so coverage of the present segments is always total.
    """
    present = {n.code: n for n in root.sorted_children()}
    used: set[str] = set()
    groups: list[LetterGroup] = []
    for letter, name, codes in LETTER_GROUPS:
        segments = [present[c] for c in codes if c in present]
        if not segments:
            continue
        used.update(s.code for s in segments)
        groups.append(
            LetterGroup(letter=letter, name=name, anchor=letter.lower(), segments=segments)
        )
    leftover = [present[c] for c in sorted(present) if c not in used]
    if leftover:
        groups.append(LetterGroup(letter="—", name="Other", anchor="other", segments=leftover))
    return groups
