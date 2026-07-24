from picasso_engine.claude_md import upsert_managed_block

BODY = "See `design-system/design-instructions.md`."
START = "<!-- picasso:start -->"
END = "<!-- picasso:end -->"

def test_appends_when_absent():
    out = upsert_managed_block("# My project\n", BODY)
    assert START in out and END in out
    assert BODY in out
    assert out.startswith("# My project")

def test_appends_to_empty_file():
    out = upsert_managed_block("", BODY)
    assert out.startswith(START)
    assert BODY in out

def test_replaces_existing_block():
    first = upsert_managed_block("# P\n", "OLD BODY")
    second = upsert_managed_block(first, "NEW BODY")
    assert "NEW BODY" in second
    assert "OLD BODY" not in second
    assert second.count(START) == 1  # not duplicated

def test_idempotent():
    once = upsert_managed_block("# P\n", BODY)
    twice = upsert_managed_block(once, BODY)
    assert once == twice

def test_preserves_content_outside_block():
    base = "# P\n\nsome notes\n"
    out = upsert_managed_block(base, BODY)
    assert "some notes" in out

def test_idempotent_when_body_contains_markers():
    body = "before <!-- picasso:end --> mid <!-- picasso:start --> after"
    once = upsert_managed_block("# P\n", body)
    twice = upsert_managed_block(once, body)
    assert once == twice

def test_single_blank_line_before_block():
    out = upsert_managed_block("# P\n", "X")
    assert "# P\n\n<!-- picasso:start -->" in out
