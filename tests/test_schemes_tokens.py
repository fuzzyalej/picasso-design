from picasso_engine.schemes import run_check

PAIR_CHECK = {
    "scheme": "token-pair",
    "pairs": [["color-text", "color-bg"]],
    "minRatio": 4.5,
}


def test_token_pair_flags_a_failing_pair():
    tokens = {"color-text": "#777777", "color-bg": "#ffffff"}
    assert run_check(PAIR_CHECK, "", "css", tokens)


def test_token_pair_passes_a_compliant_pair():
    tokens = {"color-text": "#18181b", "color-bg": "#ffffff"}
    assert run_check(PAIR_CHECK, "", "css", tokens) == []


def test_token_pair_skips_when_a_token_is_absent():
    assert run_check(PAIR_CHECK, "", "css", {"color-text": "#000001"}) == []


def test_token_pair_is_inert_without_tokens():
    assert run_check(PAIR_CHECK, "", "css", None) == []


def test_token_pair_snippet_names_both_tokens():
    tokens = {"color-text": "#777777", "color-bg": "#ffffff"}
    (_, snippet), = run_check(PAIR_CHECK, "", "css", tokens)
    assert "--color-text" in snippet and "--color-bg" in snippet


def test_external_deps_builtin_flags_a_remote_asset():
    check = {"scheme": "builtin", "name": "external_deps_check", "kinds": ["html", "css"]}
    html = '<img src="https://cdn.example.com/a.png" alt="a">'
    assert run_check(check, html, "html", {})


def test_external_deps_builtin_ignores_a_local_asset():
    check = {"scheme": "builtin", "name": "external_deps_check", "kinds": ["html", "css"]}
    assert run_check(check, '<img src="./a.png" alt="a">', "html", {}) == []


def test_external_deps_builtin_skips_copy():
    check = {"scheme": "builtin", "name": "external_deps_check", "kinds": ["html", "css"]}
    assert run_check(check, "see https://example.com", "copy", {}) == []


def test_undefined_token_refs_flags_an_unknown_token():
    check = {"scheme": "builtin", "name": "undefined_token_refs", "kinds": ["html", "css"]}
    assert run_check(check, ".x{color:var(--nope);}", "css", {"color-text": "#111"})


def test_undefined_token_refs_accepts_a_defined_token():
    check = {"scheme": "builtin", "name": "undefined_token_refs", "kinds": ["html", "css"]}
    assert run_check(check, ".x{color:var(--color-text);}", "css",
                     {"color-text": "#111"}) == []


def test_undefined_token_refs_is_inert_without_tokens():
    check = {"scheme": "builtin", "name": "undefined_token_refs", "kinds": ["html", "css"]}
    assert run_check(check, ".x{color:var(--nope);}", "css", None) == []
