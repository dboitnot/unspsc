# unspsc-cards

Generate a static, navigable website of HTML "index cards" from the UNSPSC codeset.

One card is produced per UNSPSC node (Segment → Family → Class → Commodity), laid out as a
directory tree. Cards drill down to their children via relative hyperlinks and navigate up via
breadcrumbs. The generated site is fully static and self-contained — it opens correctly both
from `file://` and from a static HTTP server.

## Quick start

```sh
just install
just build                 # reads unspsc-english-v260801.1.xlsx → ./site
just build input=other.xlsx out=public
open site/index.html       # or serve ./site with any static HTTP server
```

## Input

A UNSPSC Excel export with one row per Commodity and explicit code + title columns for each of the
four levels. The bundled file is the UNDP/UNGM English export (`UNv260801`); its header is on row
13 (rows 1–12 are a preamble). See `CLAUDE.md` for the verified column mapping and the conventions
the generator relies on.

## Development

```sh
just test        # pytest
just lint        # ruff check
just fmt         # ruff format
just typecheck   # mypy
just check       # all of the above
```
