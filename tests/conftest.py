import pytest

from unspsc_cards.model import Node, Record, build_tree


def _record(commodity_code: str, commodity_title: str, **over: object) -> Record:
    base: dict[str, object] = {
        "segment_code": "44000000",
        "segment_title": "Office Equipment and Accessories and Supplies",
        "segment_definition": "Segment def & more",
        "family_code": "44110000",
        "family_title": "Office supplies",
        "family_definition": None,
        "class_code": "44111800",
        "class_title": "Folders",
        "class_definition": None,
        "commodity_code": commodity_code,
        "commodity_title": commodity_title,
        "commodity_definition": None,
        "letter": None,
        "synonym": None,
        "acronym": None,
    }
    base.update(over)
    return Record(**base)  # type: ignore[arg-type]


@pytest.fixture
def sample_tree() -> Node:
    """root → Segment 44 → Family 4411 → Class 441118 → two Commodities."""
    return build_tree(
        [
            _record("44111810", "Hanging folders", commodity_definition="A suspension file."),
            _record("44111811", "Box files", synonym="box file", acronym="BF"),
        ]
    )
