"""Typer CLI: read the UNSPSC xlsx and generate the static card site."""

from __future__ import annotations

from pathlib import Path
from typing import Annotated

import typer

from .generate import generate_site
from .model import build_tree
from .reader import read_codeset

app = typer.Typer(add_completion=False, help="Generate a static website of UNSPSC index cards.")


@app.callback()
def main() -> None:
    """Generate a static website of UNSPSC index cards."""


@app.command()
def build(
    xlsx: Annotated[
        Path,
        typer.Argument(
            exists=True,
            dir_okay=False,
            readable=True,
            help="Path to the UNSPSC xlsx export.",
        ),
    ],
    out: Annotated[
        Path,
        typer.Option("--out", "-o", help="Output directory for the generated site."),
    ] = Path("site"),
) -> None:
    """Read XLSX and write the card site to OUT (one index.html per UNSPSC node)."""
    typer.echo(f"Reading {xlsx} ...")
    records = list(read_codeset(xlsx))
    typer.echo(f"  {len(records):,} commodity rows")
    tree = build_tree(records)
    typer.echo(f"Writing site to {out} ...")
    count = generate_site(tree, out)
    typer.echo(f"  wrote {count:,} pages (cards + A–Z index)")
    typer.echo(f"Done. Open {out / 'index.html'} in a browser, or serve {out}/ over HTTP.")
