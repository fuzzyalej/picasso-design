from picasso_engine.slop_lint import lint

def rules(findings):
    return {f.rule for f in findings}

def test_flags_em_dash_in_copy():
    assert "em-dash" in rules(lint("Build faster — ship smarter.", "copy"))

def test_flags_en_dash_in_copy():
    assert "em-dash" in rules(lint("pages 3–5 of value", "copy"))

def test_clean_copy_has_no_dash_finding():
    assert "em-dash" not in rules(lint("Build faster, ship with care.", "copy"))

def test_flags_pure_black_in_css():
    assert "pure-black" in rules(lint(".x{color:#000000;}", "css"))
    assert "pure-black" in rules(lint(".x{color:#000;}", "css"))

def test_flags_inline_hex_in_css_outside_token_decl():
    findings = lint(".btn{background:#2563eb;}", "css")
    assert "inline-hex" in rules(findings)

def test_token_declaration_line_is_allowed_hex():
    findings = lint(":root{--color-accent:#2563eb;}", "css")
    assert "inline-hex" not in rules(findings)

def test_flags_inline_hex_in_html_style():
    findings = lint('<div style="color:#2563eb">hi</div>', "html")
    assert "inline-hex" in rules(findings)

def test_inline_hex_flags_second_declaration_on_same_line():
    findings = lint(":root{--color-accent:#2563eb;background:#eeeeee;}", "css")
    assert "inline-hex" in rules(findings)

def test_inline_hex_matches_single_quoted_style():
    findings = lint("<div style='color:#2563eb'>hi</div>", "html")
    assert "inline-hex" in rules(findings)

def test_pure_black_matches_alpha_forms():
    assert "pure-black" in rules(lint(".x{color:#000f;}", "css"))
    assert "pure-black" in rules(lint(".x{color:#000000ff;}", "css"))

def test_pure_black_not_flagged_in_copy_prose():
    assert "pure-black" not in rules(lint("the hex #000 is pure black", "copy"))
