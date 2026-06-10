import re
from pathlib import Path

from unspsc_cards.generate import generate_site, is_safe_to_clear


def _resolve_all_links(page_file: Path) -> None:
    """Assert every non-anchor href in a page resolves to a real file relative to it."""
    for href in re.findall(r'href="([^"]+)"', page_file.read_text(encoding="utf-8")):
        if href.startswith("#"):
            continue
        assert (page_file.parent / href).resolve().is_file(), f"{page_file.name} -> {href}"


def test_generate_site_writes_expected_tree(tmp_path, sample_tree):
    out = tmp_path / "site"
    count = generate_site(sample_tree, out)
    assert count == 8  # 6 cards + a-z landing + 1 entry page
    for rel in [
        "index.html",
        "44/index.html",
        "44/11/index.html",
        "44/11/18/index.html",
        "44/11/18/44111810.html",  # leaf commodities are named files in the class dir
        "44/11/18/44111811.html",
    ]:
        assert (out / rel).is_file(), rel
    # the old per-commodity directories must NOT exist
    assert not (out / "44" / "11" / "18" / "10").exists()


def test_generate_site_drilldown_link_target_exists(tmp_path, sample_tree):
    out = tmp_path / "site"
    generate_site(sample_tree, out)
    class_dir = out / "44" / "11" / "18"
    # the class card links to "44111810.html" — that file must exist relative to the class dir
    assert (class_dir / "44111810.html").is_file()


def test_generate_site_breadcrumb_link_resolves_to_root(tmp_path, sample_tree):
    out = tmp_path / "site"
    generate_site(sample_tree, out)
    class_dir = out / "44" / "11" / "18"
    resolved = (class_dir / "../../../index.html").resolve()
    assert resolved == (out / "index.html").resolve()


def test_generate_site_commodity_breadcrumbs_resolve(tmp_path, sample_tree):
    out = tmp_path / "site"
    generate_site(sample_tree, out)
    commodity = out / "44" / "11" / "18" / "44111810.html"
    # class link is same-dir "index.html"; root link climbs three dirs
    assert (commodity.parent / "index.html").resolve() == (out / "44" / "11" / "18" / "index.html")
    assert (commodity.parent / "../../../index.html").resolve() == (out / "index.html").resolve()


def test_generate_site_root_index_links_to_segment(tmp_path, sample_tree):
    out = tmp_path / "site"
    generate_site(sample_tree, out)
    html = (out / "index.html").read_text(encoding="utf-8")
    assert 'href="44/index.html"' in html
    assert (out / "44" / "index.html").is_file()


def test_generate_site_clears_stale_output(tmp_path, sample_tree):
    out = tmp_path / "site"
    (out / "stale").mkdir(parents=True)
    (out / "stale" / "old.html").write_text("old", encoding="utf-8")
    generate_site(sample_tree, out)
    assert not (out / "stale").exists()  # stale content from a prior run is gone
    assert (out / "index.html").is_file()


def test_is_safe_to_clear_rejects_cwd_and_root():
    assert is_safe_to_clear(Path.cwd()) is False
    assert is_safe_to_clear(Path(Path.cwd().anchor)) is False


def test_is_safe_to_clear_allows_subdir(tmp_path):
    assert is_safe_to_clear(tmp_path / "site") is True


def test_generate_site_writes_alpha_index_and_pages(tmp_path, sample_tree):
    out = tmp_path / "site"
    generate_site(sample_tree, out)
    assert (out / "a-z" / "index.html").is_file()
    assert list((out / "a-z").glob("p*.html"))  # at least one entry page


def test_generate_site_alpha_links_resolve(tmp_path, sample_tree):
    out = tmp_path / "site"
    generate_site(sample_tree, out)
    _resolve_all_links(out / "a-z" / "index.html")  # landing: jumps + page list + home
    for page in (out / "a-z").glob("p*.html"):
        _resolve_all_links(page)  # entries + jumps + prev/next + home


def test_generate_site_index_links_to_alpha(tmp_path, sample_tree):
    out = tmp_path / "site"
    generate_site(sample_tree, out)
    assert 'href="a-z/index.html"' in (out / "index.html").read_text(encoding="utf-8")
