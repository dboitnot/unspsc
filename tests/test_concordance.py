from unspsc_cards.concordance import (
    AlphaPage,
    collect_entries,
    letter_jumps,
    paginate,
    slugify,
)
from unspsc_cards.model import Node

# --- slugify ------------------------------------------------------------------


def test_slugify_basic():
    assert slugify("Cable Assembly") == "cable-assembly"


def test_slugify_strips_punct_and_collapses_runs():
    assert slugify("  Re-bar & rod, type A  ") == "re-bar-rod-type-a"


def test_slugify_keeps_digits():
    assert slugify("100% cotton") == "100-cotton"


def test_slugify_caps_length():
    assert len(slugify("a" * 100)) <= 40


def test_slugify_all_symbols_is_empty():
    assert slugify("!!!") == ""


# --- collect_entries ----------------------------------------------------------


def test_collect_entries_includes_all_levels_sorted(sample_tree):
    titles = [n.title for n in collect_entries(sample_tree)]
    assert titles == [
        "Box files",
        "Folders",
        "Hanging folders",
        "Office Equipment and Accessories and Supplies",
        "Office supplies",
    ]


# --- paginate -----------------------------------------------------------------


def test_paginate_chunks_with_guideword_slugs(sample_tree):
    pages = paginate(collect_entries(sample_tree), page_size=2)
    assert [p.number for p in pages] == [1, 2, 3]
    assert [len(p.nodes) for p in pages] == [2, 2, 1]
    assert pages[0].slug == "p001-box-files"
    assert pages[1].slug == "p002-hanging-folders"
    assert pages[2].slug == "p003-office-supplies"


def test_paginate_slug_falls_back_when_first_title_empty():
    node = Node(code="44000000", level=1, title="!!!")
    pages = paginate([node], page_size=10)
    assert pages[0].slug == "p001"


# --- letter_jumps -------------------------------------------------------------


def test_letter_jumps_first_page_per_letter_in_order(sample_tree):
    pages = paginate(collect_entries(sample_tree), page_size=2)
    jumps = {j["label"]: j["slug"] for j in letter_jumps(pages)}
    assert jumps["B"] == "p001-box-files"  # Box files
    assert jumps["F"] == "p001-box-files"  # Folders (same page)
    assert jumps["H"] == "p002-hanging-folders"
    assert jumps["O"] == "p002-hanging-folders"  # first Office is on page 2
    assert [j["label"] for j in letter_jumps(pages)] == ["B", "F", "H", "O"]


def test_letter_jumps_symbols_bucket_last():
    letter = AlphaPage(number=1, slug="p001-apple", nodes=[Node("44000000", 1, "Apple")])
    symbol = AlphaPage(number=2, slug="p002-3d", nodes=[Node("45000000", 1, "3D printer")])
    jumps = letter_jumps([letter, symbol])
    assert [j["label"] for j in jumps] == ["A", "#"]
    assert jumps[-1]["slug"] == "p002-3d"
