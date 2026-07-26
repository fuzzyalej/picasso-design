from picasso_engine.schemes import run_check

HEX = "#[0-9a-fA-F]{3,8}\\b"


def test_strip_removes_custom_property_declarations_before_matching():
    check = {
        "scheme": "regex", "kinds": ["css"], "pattern": HEX,
        "strip": ["--[A-Za-z0-9_-]+\\s*:\\s*[^;]*;?"],
    }
    assert run_check(check, ":root{--color-accent:#2563eb;}", "css") == []


def test_strip_still_flags_a_second_non_token_declaration():
    check = {
        "scheme": "regex", "kinds": ["css"], "pattern": HEX,
        "strip": ["--[A-Za-z0-9_-]+\\s*:\\s*[^;]*;?"],
    }
    css = ":root{--color-accent:#2563eb;background:#eeeeee;}"
    assert run_check(check, css, "css")


def test_within_limits_matching_to_a_capture_group():
    check = {
        "scheme": "regex", "kinds": ["html"], "pattern": HEX, "flags": "is",
        "within": {"pattern": "style\\s*=\\s*([\"'])(.*?)\\1", "group": 2},
    }
    assert run_check(check, '<div style="color:#2563eb">hi</div>', "html")
    assert run_check(check, '<div title="#2563eb">hi</div>', "html") == []


def test_absent_suppresses_a_match_that_contains_the_pattern():
    check = {
        "scheme": "regex", "kinds": ["html"], "flags": "i",
        "pattern": "<img\\b[^>]*>", "absent": "\\balt\\s*=",
    }
    assert run_check(check, '<img src="x.png">', "html")
    assert run_check(check, '<img src="x.png" alt="A cat">', "html") == []


def test_skip_if_file_matches_stands_the_rule_down():
    check = {
        "scheme": "regex", "kinds": ["css"], "flags": "i",
        "pattern": "outline\\s*:\\s*(?:none|0)\\b",
        "skipIfFileMatches": ":focus-visible",
    }
    assert run_check(check, ".btn{outline:none;}", "css")
    css = ".btn{outline:none;} .btn:focus-visible{outline:2px solid blue;}"
    assert run_check(check, css, "css") == []
