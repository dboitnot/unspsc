"""Walk a ``Node`` tree and write one ``index.html`` per node into a nested directory tree.

A node's directory is its per-level group path (e.g. commodity ``44111810`` -> ``44/11/18/10``);
the synthetic root maps to the output directory itself. Because every card links with relative
paths, the resulting tree opens correctly from both ``file://`` and a static HTTP server.
"""

from __future__ import annotations

import shutil
from pathlib import Path

from .codes import output_path
from .concordance import collect_entries, letter_jumps, paginate
from .model import Node
from .render import render_alpha_landing, render_alpha_page, render_node


def is_safe_to_clear(path: Path) -> bool:
    """True if ``path`` may be deleted wholesale (not root, the cwd, or a cwd ancestor)."""
    resolved = path.resolve()
    cwd = Path.cwd().resolve()
    if resolved == Path(resolved.anchor):
        return False
    return not (resolved == cwd or resolved in cwd.parents)


def generate_site(root: Node, out_dir: str | Path) -> int:
    """Write the whole site under ``out_dir`` (cleared first); return the card count."""
    out = Path(out_dir)
    if out.exists():
        if not is_safe_to_clear(out):
            raise ValueError(
                f"refusing to clear {out.resolve()}: it is the "
                f"filesystem root, the current directory, or an ancestor of it"
            )
        shutil.rmtree(out)
    count = 0
    stack: list[Node] = [root]
    while stack:
        node = stack.pop()
        dir_parts, filename = output_path(node.code, node.level, is_leaf=not node.children)
        node_dir = out.joinpath(*dir_parts)
        node_dir.mkdir(parents=True, exist_ok=True)
        (node_dir / filename).write_text(render_node(node), encoding="utf-8")
        count += 1
        stack.extend(node.sorted_children())
    count += _write_alpha_index(root, out)
    return count


def _write_alpha_index(root: Node, out: Path) -> int:
    """Write the A–Z concordance under ``out/a-z`` (landing + pages); return the file count."""
    entries = collect_entries(root)
    pages = paginate(entries)
    jumps = letter_jumps(pages)
    az_dir = out / "a-z"
    az_dir.mkdir(parents=True, exist_ok=True)
    (az_dir / "index.html").write_text(
        render_alpha_landing(pages, jumps, len(entries)), encoding="utf-8"
    )
    written = 1
    for i, page in enumerate(pages):
        prev_slug = pages[i - 1].slug if i > 0 else None
        next_slug = pages[i + 1].slug if i + 1 < len(pages) else None
        (az_dir / f"{page.slug}.html").write_text(
            render_alpha_page(page, len(pages), jumps, prev_slug, next_slug), encoding="utf-8"
        )
        written += 1
    return written
