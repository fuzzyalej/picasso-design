from picasso_engine.artifact_check import external_deps, undefined_var_refs

def test_detects_external_script_and_link():
    html = '<script src="https://cdn.example.com/x.js"></script>'
    assert external_deps(html)

def test_allows_local_relative_import():
    html = '<link rel="stylesheet" href="tokens.css">'
    assert external_deps(html) == []

def test_detects_remote_url_in_css():
    css = ".x{background:url(https://img.example.com/a.png);}"
    assert external_deps(css)

def test_undefined_var_ref_flagged():
    tokens = {"color-accent": "#2563eb"}
    html = '<div style="color:var(--color-missing)"></div>'
    assert "--color-missing" in undefined_var_refs(html, tokens)

def test_defined_var_ref_ok():
    tokens = {"color-accent": "#2563eb"}
    html = '<div style="color:var(--color-accent)"></div>'
    assert undefined_var_refs(html, tokens) == []

def test_detects_quoted_url_in_css():
    assert external_deps('.x{background:url("https://img.example.com/a.png");}')
    assert external_deps(".x{background:url('https://img.example.com/a.png');}")

def test_detects_protocol_relative_src():
    assert external_deps('<script src="//cdn.example.com/x.js"></script>')

def test_detects_single_quoted_external_href():
    assert external_deps("<link href='https://cdn.example.com/a.css'>")

def test_allows_svg_fragment_and_data_uri():
    assert external_deps('<div style="background:url(#grad)"></div>') == []
    assert external_deps('<img src="data:image/png;base64,AAAA">') == []

def test_allows_root_relative_local_path():
    assert external_deps('<link href="/assets/tokens.css">') == []

def test_detects_bare_string_import():
    assert external_deps('<style>@import "https://fonts.googleapis.com/css?family=Inter";</style>')

def test_detects_import_url_form():
    assert external_deps('@import url("https://fonts.example.com/f.css");')

def test_allows_local_import():
    assert external_deps('@import "tokens.css";') == []
    assert external_deps('@import "../tokens.css";') == []

def test_detects_external_srcset():
    assert external_deps('<img srcset="https://cdn.example.com/x.jpg 2x">')

def test_allows_local_srcset():
    assert external_deps('<img srcset="hero.jpg 1x, hero@2x.jpg 2x">') == []
