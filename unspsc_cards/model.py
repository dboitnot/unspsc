"""The UNSPSC hierarchy: a flat row ``Record`` and the ``Node`` tree built from it.

The tree is assembled from the *explicit* level-code columns on each row (Segment, Family,
Class, Commodity codes are all fully-qualified 8-char codes), never by inferring levels from
trailing zeros.
"""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass, field

from .codes import display_code, group_at_level

LEVEL_NAMES = {0: "UNSPSC", 1: "Segment", 2: "Family", 3: "Class", 4: "Commodity"}


@dataclass
class Record:
    """One commodity row: a code/title/definition for each of the four levels, plus extras."""

    segment_code: str
    segment_title: str
    segment_definition: str | None
    family_code: str
    family_title: str
    family_definition: str | None
    class_code: str
    class_title: str
    class_definition: str | None
    commodity_code: str
    commodity_title: str
    commodity_definition: str | None
    letter: str | None = None
    synonym: str | None = None
    acronym: str | None = None


@dataclass
class Node:
    """A node in the UNSPSC tree (level 0 is the synthetic root; 1-4 are the levels)."""

    code: str
    level: int
    title: str
    definition: str | None = None
    letter: str | None = None
    synonym: str | None = None
    acronym: str | None = None
    parent: Node | None = None
    children: dict[str, Node] = field(default_factory=dict)

    @property
    def display(self) -> str:
        """The code formatted for display (``4411.1810`` or ``G-4411.1810``)."""
        return display_code(self.code, self.letter)

    @property
    def name(self) -> str:
        """The level label: Segment / Family / Class / Commodity."""
        return LEVEL_NAMES[self.level]

    def sorted_children(self) -> list[Node]:
        """Children ordered by code (stable, deterministic output)."""
        return sorted(self.children.values(), key=lambda n: n.code)


def _ensure_child(
    parent: Node,
    code: str,
    level: int,
    title: str,
    definition: str | None,
    letter: str | None,
    synonym: str | None = None,
    acronym: str | None = None,
) -> Node:
    key = group_at_level(code, level)
    node = parent.children.get(key)
    if node is None:
        node = Node(
            code=code,
            level=level,
            title=title,
            definition=definition,
            letter=letter,
            synonym=synonym,
            acronym=acronym,
            parent=parent,
        )
        parent.children[key] = node
    return node


def build_tree(records: Iterable[Record]) -> Node:
    """Assemble the full tree from row records, deduplicating shared ancestors."""
    root = Node(code="00000000", level=0, title=LEVEL_NAMES[0])
    for r in records:
        seg = _ensure_child(
            root, r.segment_code, 1, r.segment_title, r.segment_definition, r.letter
        )
        fam = _ensure_child(seg, r.family_code, 2, r.family_title, r.family_definition, r.letter)
        cls = _ensure_child(fam, r.class_code, 3, r.class_title, r.class_definition, r.letter)
        _ensure_child(
            cls,
            r.commodity_code,
            4,
            r.commodity_title,
            r.commodity_definition,
            r.letter,
            r.synonym,
            r.acronym,
        )
    return root
