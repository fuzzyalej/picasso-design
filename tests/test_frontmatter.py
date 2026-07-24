from picasso_engine.frontmatter import parse_frontmatter


def test_parses_simple_frontmatter():
    text = "---\nname: taste\ndescription: Do the thing.\n---\n# Body\n"
    fm = parse_frontmatter(text)
    assert fm["name"] == "taste"
    assert fm["description"] == "Do the thing."


def test_no_fence_returns_empty():
    assert parse_frontmatter("# Just a heading\n") == {}


def test_stops_at_closing_fence():
    text = "---\nname: x\n---\nname: not-this\n"
    assert parse_frontmatter(text) == {"name": "x"}
