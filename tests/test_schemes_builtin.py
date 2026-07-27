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


def test_top_level_layers_ignores_commas_inside_parens():
    from picasso_engine.schemes import top_level_layers
    assert top_level_layers("0 4px 12px rgba(24, 24, 27, 0.08)") == 1
    assert top_level_layers(
        "0 1px 2px rgba(24,24,27,0.04), 0 4px 8px rgba(24,24,27,0.05)") == 2


def test_top_level_layers_counts_a_multiline_value():
    from picasso_engine.schemes import top_level_layers
    value = ("0 1px 2px rgba(24, 24, 27, 0.04),\n"
             "             0 4px 8px rgba(24, 24, 27, 0.05),\n"
             "             0 8px 16px rgba(24, 24, 27, 0.05)")
    assert top_level_layers(value) == 3


def test_shadow_single_layer_flags_a_lone_cast():
    check = {"scheme": "builtin", "name": "shadow_single_layer", "kinds": ["css"]}
    css = ":root{--shadow-md: 0 4px 12px rgba(24, 24, 27, 0.08);}"
    assert run_check(check, css, "css") == [(1, "--shadow-md")]


def test_shadow_single_layer_accepts_a_layered_stack():
    check = {"scheme": "builtin", "name": "shadow_single_layer", "kinds": ["css"]}
    css = (":root{--shadow-md: 0 1px 2px rgba(24,24,27,0.04),\n"
           "                    0 4px 8px rgba(24,24,27,0.05);}")
    assert run_check(check, css, "css") == []


def test_shadow_single_layer_reports_the_declaration_line():
    check = {"scheme": "builtin", "name": "shadow_single_layer", "kinds": ["css"]}
    css = ":root{\n  --color-bg: #fff;\n  --shadow-sm: 0 1px 2px rgba(0,0,0,0.06);\n}"
    assert run_check(check, css, "css") == [(3, "--shadow-sm")]


def test_shadow_single_layer_ignores_non_shadow_tokens():
    check = {"scheme": "builtin", "name": "shadow_single_layer", "kinds": ["css"]}
    css = ":root{--focus-ring: 0 0 0 3px var(--color-accent-weak);}"
    assert run_check(check, css, "css") == []


def test_shadow_single_layer_ignores_an_inline_box_shadow_usage():
    check = {"scheme": "builtin", "name": "shadow_single_layer", "kinds": ["css"]}
    css = ".tabs button{box-shadow: inset 0 -2px 0 var(--color-accent);}"
    assert run_check(check, css, "css") == []


def test_shadow_single_layer_exempts_none():
    check = {"scheme": "builtin", "name": "shadow_single_layer", "kinds": ["css"]}
    assert run_check(check, ":root{--shadow-none: none;}", "css") == []


def test_shadow_single_layer_skips_html_and_copy():
    check = {"scheme": "builtin", "name": "shadow_single_layer", "kinds": ["css"]}
    css = ":root{--shadow-md: 0 4px 12px rgba(24,24,27,0.08);}"
    assert run_check(check, css, "html") == []
    assert run_check(check, css, "copy") == []


def test_shadow_single_layer_catches_a_declaration_without_a_semicolon():
    check = {"scheme": "builtin", "name": "shadow_single_layer", "kinds": ["css"]}
    css = ":root{--shadow-md: 0 4px 12px rgba(0,0,0,.1)}"
    assert run_check(check, css, "css") == [(1, "--shadow-md")]


def test_shadow_single_layer_does_not_run_past_a_closing_brace():
    check = {"scheme": "builtin", "name": "shadow_single_layer", "kinds": ["css"]}
    css = ":root{--shadow-md: 0 4px 12px rgba(0,0,0,.1)}.x{color:red}"
    assert run_check(check, css, "css") == [(1, "--shadow-md")]


def test_shadow_single_layer_still_catches_a_flat_elevation_shadow():
    # The regression guard: exemptions below must not swallow this case.
    check = {"scheme": "builtin", "name": "shadow_single_layer", "kinds": ["css"]}
    css = ":root{--shadow-md: 0 4px 12px rgba(24,24,27,0.08);}"
    assert run_check(check, css, "css") == [(1, "--shadow-md")]


def test_shadow_single_layer_exempts_a_color_helper():
    check = {"scheme": "builtin", "name": "shadow_single_layer", "kinds": ["css"]}
    css = ":root{--shadow-color: 220 3% 15%;}"
    assert run_check(check, css, "css") == []


def test_shadow_single_layer_exempts_a_bare_var_alias():
    check = {"scheme": "builtin", "name": "shadow_single_layer", "kinds": ["css"]}
    css = ":root{--shadow-card: var(--shadow-md);}"
    assert run_check(check, css, "css") == []


def test_shadow_single_layer_exempts_a_focus_ring():
    check = {"scheme": "builtin", "name": "shadow_single_layer", "kinds": ["css"]}
    css = ":root{--shadow-focus: 0 0 0 3px rgba(37,99,235,.4);}"
    assert run_check(check, css, "css") == []


def test_shadow_single_layer_exempts_a_single_inset_hairline():
    check = {"scheme": "builtin", "name": "shadow_single_layer", "kinds": ["css"]}
    css = ":root{--shadow-inset: inset 0 1px 0 rgba(255,255,255,.06);}"
    assert run_check(check, css, "css") == []


def test_shadow_single_layer_evaluates_a_multi_cast_inset_lead_on_layer_count():
    # Fix 2's inset exemption applies only to a single-cast value. A value
    # that leads with inset but has more than one cast must still be judged
    # on layer count, not waved through, or the dark tokens (Fix 4) would
    # silently stop being checked.
    check = {"scheme": "builtin", "name": "shadow_single_layer", "kinds": ["css"]}
    layered = (":root{--shadow-md: inset 0 1px 0 rgba(255,255,255,.06),"
               " 0 4px 8px rgba(0,0,0,.4);}")
    assert run_check(check, layered, "css") == []
