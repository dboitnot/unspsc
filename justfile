# justfile — task runner for unspsc-cards
# Run `just` with no args to list recipes.

default:
    @just --list

# Install all dependencies into the Poetry-managed venv.
install:
    poetry install

# Generate the card site from the UNSPSC xlsx.
# Usage: just build [input=...] [out=...]
build input="unspsc-english-v260801.1.xlsx" out="site":
    poetry run unspsc-cards build "{{ input }}" --out "{{ out }}"

# Generate the Pagefind full-text search index over an already-built site (needs pagefind on PATH).
index out="site":
    pagefind --site "{{ out }}"

# Build the site and its search index (run inside `nix develop`).
build-all input="unspsc-english-v260801.1.xlsx" out="site": (build input out) (index out)

# Serve the built site locally for preview (default http://localhost:8000).
serve out="site" port="8000":
    python3 -m http.server {{ port }} -d "{{ out }}"

# Run the test suite (pass extra args, e.g. `just test tests/test_codes.py::test_x`).
test *args:
    poetry run pytest {{ args }}

# Lint with ruff.
lint:
    poetry run ruff check .

# Auto-format with ruff.
fmt:
    poetry run ruff format .

# Static type-check the package.
typecheck:
    poetry run mypy unspsc_cards

# Lint + types + tests.
check: lint typecheck test
