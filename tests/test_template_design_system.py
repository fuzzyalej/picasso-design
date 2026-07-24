from pathlib import Path
from picasso_engine.tokens import parse_tokens
from picasso_engine.artifact_check import external_deps, undefined_var_refs
from picasso_engine.slop_lint import lint

TPL = Path(__file__).resolve().parent.parent / "templates"
HTML = (TPL / "design_system.html").read_text()
TOKENS = parse_tokens((TPL / "tokens.css").read_text())


def test_ds_self_contained():
    assert external_deps(HTML) == []


def test_ds_only_defined_tokens():
    assert undefined_var_refs(HTML, TOKENS) == []


def test_ds_imports_components():
    assert 'components.css' in HTML


def test_ds_zero_findings():
    assert lint(HTML, "html") == []


def test_ds_has_all_sections():
    low = HTML.lower()
    for marker in ("brand", "palette", "typograph", "values",
                   "contrast", "table", "modal", "empty-state", "error-state"):
        assert marker in low


def test_ds_no_dashes():
    assert "—" not in HTML and "–" not in HTML
