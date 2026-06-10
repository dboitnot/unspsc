from unspsc_cards.letters import grouped_segments
from unspsc_cards.model import Node


def _root_with_segments(*codes_titles: tuple[str, str]) -> Node:
    root = Node(code="00000000", level=0, title="UNSPSC")
    for code, title in codes_titles:
        root.children[code[:2]] = Node(code=code, level=1, title=title, parent=root)
    return root


def test_grouped_segments_orders_groups_a_to_j_and_skips_empty():
    root = _root_with_segments(
        ("44000000", "Office Equipment"),  # G
        ("10000000", "Live Plant"),  # A
        ("70000000", "Farming services"),  # J
    )
    groups = grouped_segments(root)
    assert [g.letter for g in groups] == ["A", "G", "J"]
    assert groups[0].name.startswith("Raw Materials")
    assert groups[0].anchor == "a"
    assert [s.code for s in groups[0].segments] == ["10000000"]


def test_grouped_segments_preserves_canonical_within_group_order():
    root = _root_with_segments(
        ("12000000", "Chemicals"),
        ("10000000", "Live Plant"),
        ("11000000", "Mineral"),
    )
    groups = grouped_segments(root)
    assert [s.code for s in groups[0].segments] == ["10000000", "11000000", "12000000"]


def test_grouped_segments_skips_empty_groups():
    root = _root_with_segments(("46000000", "Defense"))  # only group H present
    assert [g.letter for g in grouped_segments(root)] == ["H"]


def test_grouped_segments_collects_uncovered_into_other():
    root = _root_with_segments(
        ("10000000", "Live Plant"),  # A
        ("99000000", "Mystery segment"),  # not in any letter group
    )
    groups = grouped_segments(root)
    assert groups[0].letter == "A"
    assert groups[-1].anchor == "other"
    assert [s.code for s in groups[-1].segments] == ["99000000"]
