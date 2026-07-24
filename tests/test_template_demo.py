from pathlib import Path
from picasso_engine.tokens import parse_tokens
from picasso_engine.artifact_check import external_deps, undefined_var_refs
from picasso_engine.slop_lint import lint

TPL_DIR = Path(__file__).resolve().parent.parent / "templates"
DEMO = TPL_DIR / "demo" / "landing.html"
TOKENS = parse_tokens((TPL_DIR / "tokens.css").read_text())

def test_demo_self_contained():
    assert external_deps(DEMO.read_text()) == []

def test_demo_only_defined_tokens():
    assert undefined_var_refs(DEMO.read_text(), TOKENS) == []

def test_demo_has_all_three_states():
    html = DEMO.read_text().lower()
    assert "skeleton" in html   # loading
    assert "empty-state" in html
    assert "error-state" in html

def test_demo_not_sloppy():
    rules = {f.rule for f in lint(DEMO.read_text(), "html")}
    assert "purple-gradient" not in rules
    assert "inline-hex" not in rules
    assert "grid-1fr" not in rules

def test_demo_no_em_or_en_dash():
    text = DEMO.read_text()
    assert "—" not in text and "–" not in text

def test_demo_imports_components():
    assert "components.css" in DEMO.read_text()
