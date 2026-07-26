from picasso_engine.schemes import run_check


def hits(check, content, kind, tokens=None):
    return run_check(check, content, kind, tokens)


def test_regex_matches_and_reports_line_number():
    check = {"scheme": "regex", "kinds": ["copy"], "pattern": "foo"}
    result = hits(check, "clean line\nhas foo here", "copy")
    assert [line for line, _ in result] == [2]


def test_regex_respects_kinds():
    check = {"scheme": "regex", "kinds": ["copy"], "pattern": "foo"}
    assert hits(check, "foo", "css") == []


def test_regex_honours_ignorecase_flag():
    check = {"scheme": "regex", "kinds": ["copy"], "pattern": "foo", "flags": "i"}
    assert hits(check, "FOO", "copy")


def test_regex_snippet_is_the_stripped_line():
    check = {"scheme": "regex", "kinds": ["copy"], "pattern": "foo"}
    (_, snippet), = hits(check, "   has foo   ", "copy")
    assert snippet == "has foo"
