from pathlib import Path
from picasso_engine.tokens import parse_tokens
from picasso_engine.artifact_check import external_deps, undefined_var_refs
from picasso_engine.slop_lint import lint

TPL = Path(__file__).resolve().parent.parent / "templates"
CSS = (TPL / "components.css").read_text()
TOKENS = parse_tokens((TPL / "tokens.css").read_text())


def test_components_self_contained():
    assert external_deps(CSS) == []


def test_components_only_defined_tokens():
    assert undefined_var_refs(CSS, TOKENS) == []


def test_components_not_sloppy():
    r = {f.rule for f in lint(CSS, "css")}
    assert "inline-hex" not in r and "pure-black" not in r
    assert "purple-gradient" not in r and "focus-removed" not in r


def test_components_cover_core_classes():
    for cls in (".btn", ".field", ".input", ".table", ".modal",
                ".alert", ".card", ".badge", ".nav", ".skeleton"):
        assert cls in CSS


def test_components_no_dashes():
    assert "—" not in CSS and "–" not in CSS


def test_press_scale_token_exists():
    assert "press-scale" in TOKENS


def test_button_press_feedback_translates():
    assert "transform: translateY(1px)" in CSS


def test_press_scale_has_a_consumer_in_components_css():
    assert "transform: scale(var(--press-scale))" in CSS


def test_card_and_panel_consume_the_elevation_scale():
    assert "box-shadow: var(--shadow-sm)" in CSS
