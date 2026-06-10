import pytest

from unspsc_cards.codes import (
    ancestor_code,
    child_href,
    dir_depth,
    display_code,
    group_at_level,
    node_relpath,
    normalize_code,
    output_path,
    path_parts,
    up_href,
)


def test_normalize_int_code():
    assert normalize_code(10000000) == "10000000"


def test_normalize_float_code_drops_trailing_zero():
    assert normalize_code(10000000.0) == "10000000"


def test_normalize_string_code_passthrough():
    assert normalize_code("44111810") == "44111810"


def test_normalize_string_float_code():
    assert normalize_code("44111810.0") == "44111810"


def test_normalize_zero_pads_to_eight():
    assert normalize_code(6000000) == "06000000"


def test_normalize_strips_whitespace():
    assert normalize_code("  44111810  ") == "44111810"


def test_normalize_rejects_nan():
    with pytest.raises(ValueError):
        normalize_code(float("nan"))


def test_normalize_rejects_none():
    with pytest.raises(ValueError):
        normalize_code(None)


def test_normalize_rejects_non_numeric():
    with pytest.raises(ValueError):
        normalize_code("not-a-code")


# --- display_code -------------------------------------------------------------


def test_display_code_no_letter():
    assert display_code("44111810") == "4411.1810"


def test_display_code_with_letter():
    assert display_code("44111810", "G") == "G-4411.1810"


def test_display_code_none_letter_same_as_no_letter():
    assert display_code("44111810", None) == "4411.1810"


def test_display_code_segment():
    assert display_code("10000000") == "1000.0000"


# --- ancestor_code ------------------------------------------------------------


def test_ancestor_code_segment():
    assert ancestor_code("44111810", 1) == "44000000"


def test_ancestor_code_family():
    assert ancestor_code("44111810", 2) == "44110000"


def test_ancestor_code_class():
    assert ancestor_code("44111810", 3) == "44111800"


def test_ancestor_code_commodity_is_self():
    assert ancestor_code("44111810", 4) == "44111810"


# --- group_at_level -----------------------------------------------------------


def test_group_at_level():
    assert group_at_level("44111810", 1) == "44"
    assert group_at_level("44111810", 2) == "11"
    assert group_at_level("44111810", 3) == "18"
    assert group_at_level("44111810", 4) == "10"


# --- path_parts ---------------------------------------------------------------


def test_path_parts_commodity():
    assert path_parts("44111810", 4) == ["44", "11", "18", "10"]


def test_path_parts_class():
    assert path_parts("44111800", 3) == ["44", "11", "18"]


def test_path_parts_segment():
    assert path_parts("44000000", 1) == ["44"]


# --- link helpers -------------------------------------------------------------


def test_child_href_branch_links_to_dir_index():
    # a non-leaf child (e.g. a class under a family) -> its group dir's index.html
    assert child_href("44111800", 3, is_leaf=False) == "18/index.html"


def test_child_href_leaf_links_to_named_file():
    # a leaf child (a commodity) -> a {code}.html file in the current directory
    assert child_href("44111810", 4, is_leaf=True) == "44111810.html"


def test_output_path_branch_is_dir_index():
    assert output_path("44111800", 3, is_leaf=False) == (["44", "11", "18"], "index.html")


def test_output_path_leaf_is_named_file_in_parent_dir():
    assert output_path("44111810", 4, is_leaf=True) == (["44", "11", "18"], "44111810.html")


def test_output_path_root():
    assert output_path("00000000", 0, is_leaf=False) == ([], "index.html")


def test_dir_depth():
    assert dir_depth(0, is_leaf=False) == 0
    assert dir_depth(3, is_leaf=False) == 3
    assert dir_depth(4, is_leaf=True) == 3  # leaf commodity lives in its parent (class) dir


def test_node_relpath_leaf_commodity():
    assert node_relpath("57050205", 4, is_leaf=True) == "57/05/02/57050205.html"


def test_node_relpath_branch_class():
    assert node_relpath("44111800", 3, is_leaf=False) == "44/11/18/index.html"


def test_node_relpath_root():
    assert node_relpath("00000000", 0, is_leaf=False) == "index.html"


def test_up_href_self():
    assert up_href(0) == "index.html"


def test_up_href_one_level():
    assert up_href(1) == "../index.html"


def test_up_href_three_levels():
    assert up_href(3) == "../../../index.html"
