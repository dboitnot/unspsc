"""Render a ``Node`` to a self-contained HTML card.

All links produced here are relative (drill-down to children via ``group/index.html``, up via
``../``), so the output works identically from ``file://`` and a static HTTP server.
"""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from jinja2 import Environment, FileSystemLoader

from .codes import child_href, dir_depth, node_relpath, up_href
from .concordance import AlphaPage
from .letters import grouped_segments
from .model import LEVEL_NAMES, Node

LEVEL_PLURALS = {1: "Segments", 2: "Families", 3: "Classes", 4: "Commodities"}

_TEMPLATE_DIR = Path(__file__).parent / "templates"
_CARD_TEMPLATE = "card.html.j2"
_INDEX_TEMPLATE = "index.html.j2"
_ALPHA_PAGE_TEMPLATE = "alpha_page.html.j2"
_ALPHA_INDEX_TEMPLATE = "alpha_index.html.j2"


def _breadcrumbs(node: Node) -> list[dict[str, object]]:
    """Ancestor crumbs from root down to the node's parent, each with an up-link."""
    chain: list[Node] = []
    cur = node.parent
    while cur is not None:
        chain.append(cur)
        cur = cur.parent
    chain.reverse()
    depth = dir_depth(node.level, not node.children)
    return [
        {
            "title": a.title,
            "name": a.name,
            "display": a.display if a.level > 0 else None,
            "href": up_href(depth - a.level),
        }
        for a in chain
    ]


def _children(node: Node) -> list[dict[str, object]]:
    return [
        {
            "title": c.title,
            "name": c.name,
            "display": c.display,
            "href": child_href(c.code, c.level, not c.children),
        }
        for c in node.sorted_children()
    ]


def build_context(node: Node) -> dict[str, object]:
    """Assemble the template variables for one card."""
    display = node.display if node.level > 0 else None
    has_children = node.level < 4
    return {
        "title": node.title,
        "name": node.name,
        "display": display,
        "definition": node.definition,
        "synonym": node.synonym,
        "acronym": node.acronym,
        "breadcrumbs": _breadcrumbs(node),
        "children": _children(node),
        "child_label": LEVEL_NAMES.get(node.level + 1) if has_children else None,
        "child_label_plural": LEVEL_PLURALS.get(node.level + 1) if has_children else None,
        "page_title": f"{display} {node.title}" if display else node.title,
    }


def _alpha_entries(nodes: list[Node]) -> list[dict[str, object]]:
    return [
        {
            "title": n.title,
            "display": n.display,
            "name": n.name,
            "href": "../" + node_relpath(n.code, n.level, not n.children),
        }
        for n in nodes
    ]


def _alpha_jumps(jumps: list[dict[str, str]]) -> list[dict[str, str]]:
    return [{"label": j["label"], "href": f"{j['slug']}.html"} for j in jumps]


def build_alpha_page_context(
    page: AlphaPage,
    page_count: int,
    jumps: list[dict[str, str]],
    prev_slug: str | None,
    next_slug: str | None,
) -> dict[str, object]:
    """Assemble one A–Z concordance page: its entries, guide words, jump bar, and prev/next."""
    return {
        "entries": _alpha_entries(page.nodes),
        "guide_first": page.nodes[0].title,
        "guide_last": page.nodes[-1].title,
        "jumps": _alpha_jumps(jumps),
        "prev_href": f"{prev_slug}.html" if prev_slug else None,
        "next_href": f"{next_slug}.html" if next_slug else None,
        "page_num": page.number,
        "page_count": page_count,
        "home_href": "../index.html",
    }


def build_alpha_landing_context(
    pages: list[AlphaPage], jumps: list[dict[str, str]], total: int
) -> dict[str, object]:
    """Assemble the A–Z landing page: the jump bar, totals, and the per-page guide-word list."""
    return {
        "jumps": _alpha_jumps(jumps),
        "total": total,
        "page_count": len(pages),
        "page_list": [
            {
                "href": f"{p.slug}.html",
                "first_title": p.nodes[0].title,
                "last_title": p.nodes[-1].title,
                "count": len(p.nodes),
            }
            for p in pages
        ],
        "home_href": "../index.html",
    }


def build_index_context(root: Node) -> dict[str, object]:
    """Assemble the root index page: an A–J table of contents plus anchored category sections."""
    groups = grouped_segments(root)
    toc = [
        {"letter": g.letter, "name": g.name, "anchor": g.anchor, "count": len(g.segments)}
        for g in groups
    ]
    sections = [
        {
            "letter": g.letter,
            "name": g.name,
            "anchor": g.anchor,
            "segments": [
                {
                    "title": s.title,
                    "display": s.display,
                    "href": child_href(s.code, 1, not s.children),
                }
                for s in g.segments
            ],
        }
        for g in groups
    ]
    return {
        "title": "UNSPSC",
        "toc": toc,
        "sections": sections,
        "segment_count": sum(len(g.segments) for g in groups),
        "group_count": len(groups),
        "alpha_href": "a-z/index.html",
    }


@lru_cache(maxsize=1)
def _environment() -> Environment:
    return Environment(
        loader=FileSystemLoader(str(_TEMPLATE_DIR)),
        autoescape=True,
        trim_blocks=True,
        lstrip_blocks=True,
    )


def render_node(node: Node, env: Environment | None = None) -> str:
    """Render ``node`` to a complete HTML document (the root uses the grouped index page)."""
    environment = env or _environment()
    if node.level == 0:
        return environment.get_template(_INDEX_TEMPLATE).render(**build_index_context(node))
    return environment.get_template(_CARD_TEMPLATE).render(**build_context(node))


def render_alpha_page(
    page: AlphaPage,
    page_count: int,
    jumps: list[dict[str, str]],
    prev_slug: str | None,
    next_slug: str | None,
    env: Environment | None = None,
) -> str:
    """Render one A–Z concordance page to HTML."""
    environment = env or _environment()
    ctx = build_alpha_page_context(page, page_count, jumps, prev_slug, next_slug)
    return environment.get_template(_ALPHA_PAGE_TEMPLATE).render(**ctx)


def render_alpha_landing(
    pages: list[AlphaPage],
    jumps: list[dict[str, str]],
    total: int,
    env: Environment | None = None,
) -> str:
    """Render the A–Z landing page to HTML."""
    environment = env or _environment()
    return environment.get_template(_ALPHA_INDEX_TEMPLATE).render(
        **build_alpha_landing_context(pages, jumps, total)
    )
