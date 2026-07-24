from picasso_engine.tokens import parse_tokens

def test_parses_root_custom_properties():
    css = ":root {\n  --color-accent: #2563eb;\n  --space-2: 8px;\n}"
    toks = parse_tokens(css)
    assert toks["color-accent"] == "#2563eb"
    assert toks["space-2"] == "8px"

def test_ignores_non_custom_properties():
    css = ":root { --x: 1px; }\n.foo { color: red; }"
    assert parse_tokens(css) == {"x": "1px"}
