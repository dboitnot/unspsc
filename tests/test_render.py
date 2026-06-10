from unspsc_cards.concordance import collect_entries, letter_jumps, paginate
from unspsc_cards.model import Node
from unspsc_cards.render import (
    build_alpha_landing_context,
    build_alpha_page_context,
    build_context,
    build_index_context,
    render_alpha_landing,
    render_alpha_page,
    render_node,
)


def _seg(t: Node) -> Node:
    return t.sorted_children()[0]


def _fam(t: Node) -> Node:
    return _seg(t).sorted_children()[0]


def _cls(t: Node) -> Node:
    return _fam(t).sorted_children()[0]


def _com(t: Node, i: int = 0) -> Node:
    return _cls(t).sorted_children()[i]


def test_context_class_children_links(sample_tree):
    ctx = build_context(_cls(sample_tree))
    # children are leaf commodities -> linked as {code}.html files in the class dir
    assert {c["href"] for c in ctx["children"]} == {"44111810.html", "44111811.html"}
    assert ctx["child_label"] == "Commodity"


def test_context_class_breadcrumb_hrefs(sample_tree):
    ctx = build_context(_cls(sample_tree))
    crumbs = ctx["breadcrumbs"]
    assert [c["name"] for c in crumbs] == ["UNSPSC", "Segment", "Family"]
    assert crumbs[0]["href"] == "../../../index.html"  # root: 3 up from a class
    assert crumbs[1]["href"] == "../../index.html"  # segment: 2 up
    assert crumbs[2]["href"] == "../index.html"  # family: 1 up


def test_context_commodity_is_leaf(sample_tree):
    ctx = build_context(_com(sample_tree))
    assert ctx["display"] == "4411.1810"
    assert ctx["children"] == []
    assert ctx["child_label"] is None


def test_context_commodity_breadcrumb_hrefs(sample_tree):
    # a commodity file lives in its class dir, so its up-links are one level shallower
    crumbs = build_context(_com(sample_tree))["breadcrumbs"]
    assert [c["name"] for c in crumbs] == ["UNSPSC", "Segment", "Family", "Class"]
    assert crumbs[0]["href"] == "../../../index.html"  # root
    assert crumbs[1]["href"] == "../../index.html"  # segment
    assert crumbs[2]["href"] == "../index.html"  # family
    assert crumbs[3]["href"] == "index.html"  # class (same directory)


def test_context_root_lists_segments(sample_tree):
    ctx = build_context(sample_tree)
    assert ctx["display"] is None
    assert ctx["breadcrumbs"] == []
    assert [c["href"] for c in ctx["children"]] == ["44/index.html"]
    assert ctx["child_label"] == "Segment"


def test_render_node_contains_title_code_and_links(sample_tree):
    html = render_node(_cls(sample_tree))
    assert "Folders" in html
    assert "4411.1800" in html
    assert 'href="44111810.html"' in html  # leaf commodity drill-down
    assert 'href="44111811.html"' in html
    assert 'href="../../../index.html"' in html  # breadcrumb up to root (class is depth 3)


def test_render_node_escapes_html(sample_tree):
    html = render_node(_seg(sample_tree))
    assert "Segment def &amp; more" in html
    assert "Segment def & more" not in html


def test_render_node_shows_synonym_and_acronym(sample_tree):
    html = render_node(_com(sample_tree, 1))  # "Box files" carries synonym + acronym
    assert "box file" in html
    assert "BF" in html


# --- root index page (A–J letter grouping) ------------------------------------


def test_index_context_toc_and_section_for_present_group(sample_tree):
    ctx = build_index_context(sample_tree)  # one segment 44 -> category G
    assert [t["anchor"] for t in ctx["toc"]] == ["g"]
    assert ctx["toc"][0]["letter"] == "G"
    assert ctx["toc"][0]["count"] == 1
    section = ctx["sections"][0]
    assert section["anchor"] == "g"
    assert section["segments"][0]["href"] == "44/index.html"
    assert "Office Equipment" in section["segments"][0]["title"]


def test_render_root_uses_index_template_with_toc_and_anchors(sample_tree):
    html = render_node(sample_tree)
    assert 'href="#g"' in html  # TOC link to the category
    assert 'id="g"' in html  # the anchored heading it jumps to
    assert 'href="44/index.html"' in html  # segment drill-down link
    assert "Business, Communication" in html  # category G name


def test_render_segment_is_card_not_index(sample_tree):
    html = render_node(_seg(sample_tree))
    assert 'href="#g"' not in html
    assert "Office Equipment" in html


def test_index_context_has_alpha_href(sample_tree):
    assert build_index_context(sample_tree)["alpha_href"] == "a-z/index.html"


# --- alpha (A–Z concordance) contexts -----------------------------------------


def test_alpha_page_context_entries_guidewords_and_nav(sample_tree):
    pages = paginate(collect_entries(sample_tree), page_size=2)
    jumps = letter_jumps(pages)
    ctx = build_alpha_page_context(
        pages[1],
        page_count=len(pages),
        jumps=jumps,
        prev_slug=pages[0].slug,
        next_slug=pages[2].slug,
    )
    assert ctx["page_num"] == 2
    assert ctx["page_count"] == 3
    assert ctx["guide_first"] == "Hanging folders"
    assert ctx["guide_last"] == "Office Equipment and Accessories and Supplies"
    assert ctx["prev_href"] == "p001-box-files.html"
    assert ctx["next_href"] == "p003-office-supplies.html"
    assert ctx["home_href"] == "../index.html"
    hrefs = [e["href"] for e in ctx["entries"]]
    assert hrefs[0] == "../44/11/18/44111810.html"  # Hanging folders (leaf commodity)
    assert hrefs[1] == "../44/index.html"  # Office Equipment (branch segment)
    assert ctx["jumps"][0] == {"label": "B", "href": "p001-box-files.html"}


def test_alpha_page_context_prev_next_none_at_ends(sample_tree):
    pages = paginate(collect_entries(sample_tree), page_size=2)
    jumps = letter_jumps(pages)
    first = build_alpha_page_context(
        pages[0], len(pages), jumps, prev_slug=None, next_slug=pages[1].slug
    )
    last = build_alpha_page_context(
        pages[2], len(pages), jumps, prev_slug=pages[1].slug, next_slug=None
    )
    assert first["prev_href"] is None
    assert last["next_href"] is None


def test_alpha_landing_context(sample_tree):
    pages = paginate(collect_entries(sample_tree), page_size=2)
    jumps = letter_jumps(pages)
    ctx = build_alpha_landing_context(pages, jumps, total=5)
    assert ctx["total"] == 5
    assert ctx["page_count"] == 3
    assert [p["href"] for p in ctx["page_list"]][0] == "p001-box-files.html"
    assert ctx["page_list"][0]["first_title"] == "Box files"
    assert ctx["page_list"][0]["last_title"] == "Folders"
    assert ctx["page_list"][0]["count"] == 2
    assert {j["label"] for j in ctx["jumps"]} == {"B", "F", "H", "O"}


def test_render_alpha_page_html(sample_tree):
    pages = paginate(collect_entries(sample_tree), page_size=2)
    jumps = letter_jumps(pages)
    html = render_alpha_page(
        pages[1], len(pages), jumps, prev_slug=pages[0].slug, next_slug=pages[2].slug
    )
    assert 'href="../44/11/18/44111810.html"' in html  # entry → card
    assert 'href="p001-box-files.html"' in html  # prev + B jump
    assert 'href="p003-office-supplies.html"' in html  # next
    assert "Hanging folders" in html
    assert "Page 2 of 3" in html


def test_render_alpha_landing_html(sample_tree):
    pages = paginate(collect_entries(sample_tree), page_size=2)
    jumps = letter_jumps(pages)
    html = render_alpha_landing(pages, jumps, total=5)
    assert 'href="p001-box-files.html"' in html
    assert "Box files" in html
    assert "5 entries" in html


def test_render_index_has_alpha_cta(sample_tree):
    assert 'href="a-z/index.html"' in render_node(sample_tree)
