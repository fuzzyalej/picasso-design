from picasso_engine.schemes import run_check, class_families, component_use_cases
from picasso_engine.tokens import PATH_KEY, parse_tokens


def hits(content, kind, tokens=None):
    return list(component_use_cases(content, kind, tokens))


def test_class_families_extracts_base_classes():
    css = ".btn{}\n.btn--ghost{}\n.card{}\n.card__title{}\n"
    assert set(class_families(css)) == {"btn", "card"}


def test_class_families_ignores_state_and_utility_classes():
    css = ".is-invalid{}\n.btn{}\n"
    assert set(class_families(css)) == {"btn"}


def test_class_families_splits_comma_joined_selectors():
    css = ".input, .select, .textarea {}\n.card, .panel {}\n"
    assert set(class_families(css)) == {"input", "select", "textarea", "card", "panel"}


def test_class_families_ignores_descendant_and_pseudo_selectors():
    css = (
        ".field .hint {}\n"
        ".table th {}\n"
        ".nav a {}\n"
        ".btn:hover {}\n"
        ".field.is-invalid .input {}\n"
    )
    assert set(class_families(css)) == {"field", "table", "nav", "btn"}


def test_class_families_ignores_leading_dots_in_declaration_values():
    css = ".x { transition: opacity .2s, transform .2s; margin: .5rem; }\n"
    assert set(class_families(css)) == {"x"}


def test_flags_a_marker_that_only_appears_after_the_last_not_for_line(tmp_path):
    (tmp_path / "components.css").write_text(".btn{}\n", encoding="utf-8")
    design = tmp_path / "design.md"
    design.write_text(
        "## 4. Component Stylings\n"
        "- Field `.field`: label, input, hint.\n"
        "  Not for: read-only display, use `.table`.\n"
        "- Button: solid.\n"
        "  Uses `.btn` under the hood.\n",
        encoding="utf-8",
    )
    result = hits(design.read_text(encoding="utf-8"), "copy",
                  {PATH_KEY: str(design)})
    assert any("btn" in snippet for _, snippet in result)


def test_does_not_treat_a_not_for_target_as_documenting_the_base_class(tmp_path):
    (tmp_path / "components.css").write_text(".btn{}\n", encoding="utf-8")
    design = tmp_path / "design.md"
    design.write_text(
        "## 4. Component Stylings\n"
        "- Badge `.badge`: status label.\n"
        "  Not for: primary actions, use `.btn--danger`.\n",
        encoding="utf-8",
    )
    result = hits(design.read_text(encoding="utf-8"), "copy",
                  {PATH_KEY: str(design)})
    assert any("btn" == snippet for _, snippet in result)


def test_flags_a_component_with_no_not_for_line(tmp_path):
    (tmp_path / "components.css").write_text(".btn{}\n.card{}\n", encoding="utf-8")
    design = tmp_path / "design.md"
    design.write_text("## 4. Component Stylings\n- Button: solid.\n  Not for: destructive actions, use `.btn--danger`.\n",
                      encoding="utf-8")
    result = hits(design.read_text(encoding="utf-8"), "copy",
                  {PATH_KEY: str(design)})
    assert any("card" in snippet for _, snippet in result)


def test_silent_when_every_component_is_documented(tmp_path):
    (tmp_path / "components.css").write_text(".btn{}\n", encoding="utf-8")
    design = tmp_path / "design.md"
    design.write_text("## 4. Component Stylings\n- Button `.btn`: solid.\n  Not for: destructive actions, use `.btn--danger`.\n",
                      encoding="utf-8")
    assert hits(design.read_text(encoding="utf-8"), "copy",
                {PATH_KEY: str(design)}) == []


def test_inert_without_a_path_hint():
    assert hits("## 4. Component Stylings\n", "copy", {}) == []


def test_inert_on_non_copy_kinds(tmp_path):
    """The declared kinds gate this, so it must be exercised through run_check."""
    (tmp_path / "components.css").write_text(".btn{}\n", encoding="utf-8")
    design = tmp_path / "design.md"
    design.write_text("## 4. Component Stylings\n", encoding="utf-8")
    check = {"scheme": "builtin", "name": "component_use_cases", "kinds": ["copy"]}
    tokens = {PATH_KEY: str(design)}
    assert run_check(check, design.read_text(encoding="utf-8"), "css", tokens) == []
    assert run_check(check, design.read_text(encoding="utf-8"), "copy", tokens)


def test_marker_on_a_continuation_line_still_documents_the_family(tmp_path):
    (tmp_path / "components.css").write_text(".btn{}\n", encoding="utf-8")
    design = tmp_path / "design.md"
    design.write_text(
        "## 4. Component Stylings\n"
        "- Button: solid fill.\n"
        "  Uses `.btn` under the hood.\n"
        "  Not for: destructive actions, use `.btn--danger`.\n",
        encoding="utf-8",
    )
    assert hits(design.read_text(encoding="utf-8"), "copy",
                {PATH_KEY: str(design)}) == []


def test_a_css_token_named___path___cannot_impersonate_the_sentinel(tmp_path):
    (tmp_path / "components.css").write_text(".btn{}\n.card{}\n", encoding="utf-8")
    design = tmp_path / "design.md"
    design.write_text(
        "## 4. Component Stylings\n"
        "- Button `.btn`: solid.\n"
        "  Not for: destructive actions, use `.btn--danger`.\n",
        encoding="utf-8",
    )
    tokens = parse_tokens(":root{--__path__: #fff;}")
    tokens["__path__"] = str(design)  # the old sentinel name, now just a token
    result = hits(design.read_text(encoding="utf-8"), "copy", tokens)
    # Without the real PATH_KEY sentinel, the check has no design.md path
    # hint and must stay inert rather than being fooled by a same-named token.
    assert result == []
