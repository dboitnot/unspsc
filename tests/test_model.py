from unspsc_cards.model import Record, build_tree


def make_record(commodity_code: str, commodity_title: str, **over: object) -> Record:
    base: dict[str, object] = {
        "segment_code": "44000000",
        "segment_title": "Office Equipment",
        "segment_definition": "seg def",
        "family_code": "44110000",
        "family_title": "Office supplies",
        "family_definition": "fam def",
        "class_code": "44111800",
        "class_title": "Folders",
        "class_definition": "cls def",
        "commodity_code": commodity_code,
        "commodity_title": commodity_title,
        "commodity_definition": "com def",
        "letter": None,
        "synonym": None,
        "acronym": None,
    }
    base.update(over)
    return Record(**base)  # type: ignore[arg-type]


def test_build_tree_creates_four_levels():
    root = build_tree([make_record("44111810", "Hanging folders")])
    seg = root.sorted_children()[0]
    fam = seg.sorted_children()[0]
    cls = fam.sorted_children()[0]
    com = cls.sorted_children()[0]
    assert (seg.code, seg.level, seg.title) == ("44000000", 1, "Office Equipment")
    assert (fam.code, fam.level) == ("44110000", 2)
    assert (cls.code, cls.level) == ("44111800", 3)
    assert (com.code, com.level, com.title) == ("44111810", 4, "Hanging folders")
    assert com.definition == "com def"


def test_build_tree_dedupes_shared_ancestors():
    root = build_tree(
        [
            make_record("44111810", "Hanging folders"),
            make_record("44111811", "Box files"),
        ]
    )
    assert len(root.sorted_children()) == 1  # one segment
    seg = root.sorted_children()[0]
    cls = seg.sorted_children()[0].sorted_children()[0]
    assert len(cls.sorted_children()) == 2  # two commodities under one class


def test_build_tree_sets_parent_pointers():
    root = build_tree([make_record("44111810", "Hanging folders")])
    seg = root.sorted_children()[0]
    com = seg.sorted_children()[0].sorted_children()[0].sorted_children()[0]
    assert seg.parent is root
    assert com.parent.parent.parent.parent is root  # type: ignore[union-attr]
    assert root.parent is None


def test_build_tree_children_sorted_by_code():
    root = build_tree(
        [
            make_record("44111811", "Box files"),
            make_record("44111810", "Hanging folders"),
        ]
    )
    cls = root.sorted_children()[0].sorted_children()[0].sorted_children()[0]
    assert [c.code for c in cls.sorted_children()] == ["44111810", "44111811"]


def test_node_display_no_letter():
    root = build_tree([make_record("44111810", "Hanging folders")])
    com = root.sorted_children()[0].sorted_children()[0].sorted_children()[0].sorted_children()[0]
    assert com.display == "4411.1810"


def test_node_display_with_letter():
    root = build_tree([make_record("44111810", "Hanging folders", letter="G")])
    seg = root.sorted_children()[0]
    assert seg.letter == "G"
    com = seg.sorted_children()[0].sorted_children()[0].sorted_children()[0]
    assert com.display == "G-4411.1810"


def test_node_name_is_level_label():
    root = build_tree([make_record("44111810", "Hanging folders")])
    seg = root.sorted_children()[0]
    com = seg.sorted_children()[0].sorted_children()[0].sorted_children()[0]
    assert seg.name == "Segment"
    assert com.name == "Commodity"


def test_commodity_keeps_synonym_and_acronym():
    root = build_tree([make_record("44111810", "Hanging folders", synonym="suspension files")])
    com = root.sorted_children()[0].sorted_children()[0].sorted_children()[0].sorted_children()[0]
    assert com.synonym == "suspension files"
