"""Alphabetical concordance: collect every node, sort by title, and slice into even pages.

The title distribution is too clustered for prefix-based paging (thousands of titles share long
word-prefixes), so pages are fixed-size slices of the globally sorted list, each identified by its
page number plus the slugified first title (a guide word) and navigated with an A–Z jump bar.
"""

from __future__ import annotations

import re
from collections.abc import Iterator
from dataclasses import dataclass

from .model import Node

PAGE_SIZE = 1500

_SLUG_RE = re.compile(r"[^a-z0-9]+")


def slugify(text: str, max_length: int = 40) -> str:
    """Lowercase, collapse non-alphanumeric runs to ``-``, trim, and length-cap."""
    slug = _SLUG_RE.sub("-", text.lower()).strip("-")
    if len(slug) > max_length:
        slug = slug[:max_length].rstrip("-")
    return slug


def _walk(node: Node) -> Iterator[Node]:
    for child in node.children.values():
        yield child
        yield from _walk(child)


def collect_entries(root: Node) -> list[Node]:
    """Every node below the root (levels 1–4), sorted by ``(title casefold, code)``."""
    entries = list(_walk(root))
    entries.sort(key=lambda n: (n.title.casefold(), n.code))
    return entries


@dataclass
class AlphaPage:
    number: int
    slug: str
    nodes: list[Node]


def paginate(entries: list[Node], page_size: int = PAGE_SIZE) -> list[AlphaPage]:
    """Slice sorted ``entries`` into pages; slug = ``p{NNN}-{slug of first title}``."""
    pages: list[AlphaPage] = []
    for start in range(0, len(entries), page_size):
        chunk = entries[start : start + page_size]
        number = start // page_size + 1
        first = slugify(chunk[0].title)
        slug = f"p{number:03d}-{first}" if first else f"p{number:03d}"
        pages.append(AlphaPage(number=number, slug=slug, nodes=chunk))
    return pages


def _bucket(title: str) -> str:
    ch = title.strip()[:1].upper()
    return ch if "A" <= ch <= "Z" else "#"


def letter_jumps(pages: list[AlphaPage]) -> list[dict[str, str]]:
    """For each present bucket (A–Z then ``#``), the slug of the first page containing it."""
    first_slug: dict[str, str] = {}
    for page in pages:
        for node in page.nodes:
            first_slug.setdefault(_bucket(node.title), page.slug)
    order = [chr(c) for c in range(ord("A"), ord("Z") + 1)] + ["#"]
    return [{"label": k, "slug": first_slug[k]} for k in order if k in first_slug]
