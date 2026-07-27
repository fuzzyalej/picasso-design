from picasso_engine.slop_lint import lint

def rules(findings):
    return {f.rule for f in findings}

def test_flags_purple_gradient_by_keyword():
    css = ".hero{background:linear-gradient(90deg, indigo, purple);}"
    assert "purple-gradient" in rules(lint(css, "css"))

def test_flags_purple_gradient_by_hex():
    css = ".hero{background:linear-gradient(90deg,#6366f1,#a855f7);}"
    assert "purple-gradient" in rules(lint(css, "css"))

def test_non_purple_gradient_ok():
    css = ".hero{background:linear-gradient(90deg,#0f172a,#1e293b);}"
    assert "purple-gradient" not in rules(lint(css, "css"))

def test_flags_eyebrow_overuse():
    # 2 sections -> ceil(2/3)=1 allowed; 3 all-caps kickers -> flag
    html = (
        "<section><p>SELECTED WORK</p></section>"
        "<section><p>WHAT WE DO</p><p>OUR PROCESS</p></section>"
    )
    assert "eyebrow-overuse" in rules(lint(html, "html"))

def test_eyebrow_within_budget_ok():
    html = "<section><p>SELECTED WORK</p></section><section><p>hello</p></section>"
    assert "eyebrow-overuse" not in rules(lint(html, "html"))

def test_flags_fake_metric():
    assert "fake-metric" in rules(lint("+47% conversion in weeks", "copy"))
    assert "fake-metric" in rules(lint("Trusted by 50,000+ teams", "copy"))
    assert "fake-metric" in rules(lint("99.99% uptime guaranteed", "copy"))

def test_real_prose_not_flagged_as_metric():
    assert "fake-metric" not in rules(lint("We ship carefully and often.", "copy"))

def test_flags_grid_1fr_without_minmax():
    css = ".g{grid-template-columns:repeat(3,1fr);}"
    assert "grid-1fr" in rules(lint(css, "css"))

def test_minmax_grid_ok():
    css = ".g{grid-template-columns:repeat(3,minmax(0,1fr));}"
    assert "grid-1fr" not in rules(lint(css, "css"))

def test_flags_duplicate_cta():
    html = '<a class="btn">Get started</a><a class="btn">Get Started</a>'
    assert "duplicate-cta" in rules(lint(html, "html"))

def test_distinct_ctas_ok():
    html = '<a class="btn">Get started</a><a class="btn">See pricing</a>'
    assert "duplicate-cta" not in rules(lint(html, "html"))

def test_duplicate_cta_ignores_generic_card_links_without_cta_class():
    html = '<a class="card-link">Learn more</a><a class="card-link">Learn more</a>'
    assert "duplicate-cta" not in rules(lint(html, "html"))

def test_duplicate_cta_detects_icon_decorated_buttons():
    html = '<a class="btn">Get started<svg></svg></a><a class="btn">Get started<svg></svg></a>'
    assert "duplicate-cta" in rules(lint(html, "html"))

def test_grid_1fr_without_trailing_semicolon():
    assert "grid-1fr" in rules(lint(".g{grid-template-columns:repeat(3,1fr)}", "css"))

def test_fake_metric_ignores_truthful_decimal_percent():
    assert "fake-metric" not in rules(lint("Battery uses 3.7% less power.", "copy"))

def test_purple_gradient_with_nested_rgba_stop():
    css = ".h{background:linear-gradient(180deg, rgba(0,0,0,.2), purple);}"
    assert "purple-gradient" in rules(lint(css, "css"))

def test_flags_img_without_alt():
    assert "img-alt" in rules(lint('<img src="x.png">', "html"))

def test_img_with_alt_ok():
    assert "img-alt" not in rules(lint('<img src="x.png" alt="A cat">', "html"))
    assert "img-alt" not in rules(lint('<img src="x.png" alt="">', "html"))

def test_flags_focus_removed_without_focus_visible():
    css = ".btn{outline:none;}"
    assert "focus-removed" in rules(lint(css, "css"))

def test_focus_removed_ok_when_focus_visible_present():
    css = ".btn{outline:none;} .btn:focus-visible{outline:2px solid blue;}"
    assert "focus-removed" not in rules(lint(css, "css"))

def test_flags_clickable_nonsemantic_div():
    assert "clickable-nonsemantic" in rules(lint('<div onclick="go()">Go</div>', "html"))

def test_clickable_ok_with_role():
    html = '<div role="button" tabindex="0" onclick="go()">Go</div>'
    assert "clickable-nonsemantic" not in rules(lint(html, "html"))


def test_flags_maxheight_reveal_shorthand():
    css = ".acc{overflow:hidden;transition:max-height 200ms var(--ease-out);}"
    assert "maxheight-reveal" in rules(lint(css, "css"))


def test_flags_maxheight_reveal_longhand():
    css = ".acc{transition-property: max-height, opacity;}"
    assert "maxheight-reveal" in rules(lint(css, "css"))


def test_flags_maxheight_reveal_in_an_inline_style_block():
    html = "<style>.acc{transition:max-height 200ms ease-out;}</style>"
    assert "maxheight-reveal" in rules(lint(html, "html"))


def test_static_max_height_is_not_a_reveal():
    css = ".acc{max-height:400px;overflow:auto;}"
    assert "maxheight-reveal" not in rules(lint(css, "css"))


def test_grid_rows_reveal_is_clean():
    css = ".acc{display:grid;grid-template-rows:0fr;transition:grid-template-rows 200ms var(--ease-out);}"
    assert "maxheight-reveal" not in rules(lint(css, "css"))
