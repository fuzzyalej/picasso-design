from pathlib import Path
from picasso_engine.tokens import parse_tokens
from picasso_engine.artifact_check import external_deps, undefined_var_refs
from picasso_engine.slop_lint import lint

TPL_DIR = Path(__file__).resolve().parent.parent / "templates"
TOKENS = parse_tokens((TPL_DIR / "tokens.css").read_text())

import pytest

@pytest.mark.parametrize("name", ["styleguide.html", "brandbook.html"])
def test_self_contained(name):
    html = (TPL_DIR / name).read_text()
    assert external_deps(html) == []

@pytest.mark.parametrize("name", ["styleguide.html", "brandbook.html"])
def test_only_defined_tokens(name):
    html = (TPL_DIR / name).read_text()
    assert undefined_var_refs(html, TOKENS) == []

@pytest.mark.parametrize("name", ["styleguide.html", "brandbook.html"])
def test_not_sloppy(name):
    html = (TPL_DIR / name).read_text()
    rules = {f.rule for f in lint(html, "html")}
    assert "inline-hex" not in rules
    assert "pure-black" not in rules

def test_styleguide_shows_interaction_states():
    html = (TPL_DIR / "styleguide.html").read_text().lower()
    for state in ("hover", "focus-visible", "active", "disabled", "loading", "error", "success"):
        assert state in html

@pytest.mark.parametrize("name", ["styleguide.html", "brandbook.html"])
def test_no_em_or_en_dash(name):
    text = (TPL_DIR / name).read_text()
    assert "—" not in text and "–" not in text
