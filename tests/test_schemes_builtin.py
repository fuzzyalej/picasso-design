from picasso_engine.schemes import BUILTINS, run_check


def test_registry_exposes_the_four_migrated_builtins():
    for name in ("purple_gradient", "eyebrow_overuse", "grid_1fr", "duplicate_cta"):
        assert name in BUILTINS


def test_unknown_builtin_name_yields_no_hits():
    assert run_check({"scheme": "builtin", "name": "nope", "kinds": ["css"]}, "x", "css") == []


def test_purple_gradient_detects_keyword_and_hex():
    check = {"scheme": "builtin", "name": "purple_gradient", "kinds": ["html", "css"]}
    assert run_check(check, ".h{background:linear-gradient(90deg,indigo,purple);}", "css")
    assert run_check(check, ".h{background:linear-gradient(90deg,#6366f1,#a855f7);}", "css")


def test_purple_gradient_ignores_a_neutral_gradient():
    check = {"scheme": "builtin", "name": "purple_gradient", "kinds": ["html", "css"]}
    assert run_check(check, ".h{background:linear-gradient(90deg,#0f172a,#1e293b);}", "css") == []


def test_purple_gradient_skips_copy():
    check = {"scheme": "builtin", "name": "purple_gradient", "kinds": ["html", "css"]}
    assert run_check(check, "a purple gradient in prose", "copy") == []


def test_eyebrow_overuse_uses_a_section_budget():
    check = {"scheme": "builtin", "name": "eyebrow_overuse", "kinds": ["html"]}
    over = ("<section><p>SELECTED WORK</p></section>"
            "<section><p>WHAT WE DO</p><p>OUR PROCESS</p></section>")
    assert run_check(check, over, "html")
    within = "<section><p>SELECTED WORK</p></section><section><p>hello</p></section>"
    assert run_check(check, within, "html") == []


def test_grid_1fr_wants_minmax():
    check = {"scheme": "builtin", "name": "grid_1fr", "kinds": ["html", "css"]}
    assert run_check(check, ".g{grid-template-columns:repeat(3,1fr);}", "css")
    assert run_check(check, ".g{grid-template-columns:repeat(3,minmax(0,1fr));}", "css") == []


def test_duplicate_cta_needs_a_cta_class():
    check = {"scheme": "builtin", "name": "duplicate_cta", "kinds": ["html"]}
    dupe = '<a class="btn">Get started</a><a class="btn">Get Started</a>'
    assert run_check(check, dupe, "html")
    plain = '<a class="card-link">Learn more</a><a class="card-link">Learn more</a>'
    assert run_check(check, plain, "html") == []
