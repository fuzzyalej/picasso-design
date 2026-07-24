# tests/test_template_tokens.py
from pathlib import Path
from picasso_engine.tokens import parse_tokens
from picasso_engine.slop_lint import lint

TPL = Path(__file__).resolve().parent.parent / "templates" / "tokens.css"

def test_defines_all_token_groups():
    toks = parse_tokens(TPL.read_text())
    for prefix in ("color-", "font-", "space-", "size-", "radius-", "shadow-", "duration-", "ease-"):
        assert any(k.startswith(prefix) for k in toks), f"missing group {prefix}"

def test_defines_single_accent():
    toks = parse_tokens(TPL.read_text())
    assert "color-accent" in toks

def test_template_is_not_sloppy():
    findings = lint(TPL.read_text(), "css")
    rules = {f.rule for f in findings}
    assert "pure-black" not in rules
    assert "purple-gradient" not in rules
    assert "inline-hex" not in rules  # every hex is inside a --token: declaration

def test_tokens_css_no_em_or_en_dash():
    text = TPL.read_text()
    assert "—" not in text and "–" not in text
