import json
import os
from picasso_engine.rules import (
    Criterion, RULES_VERSION, merge, load_raw, load_rules, find_project_rules,
)


def crit(identifier, **over):
    values = dict(
        identifier=identifier, title="T", statement="S",
        level="must-not", category="content", verification="manual",
    )
    values.update(over)
    return Criterion(**values)


def write(tmp_path, name, payload):
    path = tmp_path / name
    path.write_text(json.dumps(payload), encoding="utf-8")
    return str(path)


def test_merge_appends_new_identifier():
    result = merge([crit("a")], [crit("b")])
    assert [c.identifier for c in result] == ["a", "b"]


def test_merge_overrides_existing_identifier_in_place():
    result = merge([crit("a", title="core"), crit("b")], [crit("a", title="project")])
    assert [c.identifier for c in result] == ["a", "b"]
    assert result[0].title == "project"


def test_merge_removes_disabled_rule():
    result = merge([crit("a"), crit("b")], [crit("a", disabled=True)])
    assert [c.identifier for c in result] == ["b"]


def test_merge_ignores_disabled_stub_for_unknown_identifier():
    result = merge([crit("a")], [crit("zzz", disabled=True)])
    assert [c.identifier for c in result] == ["a"]


def test_load_raw_reports_missing_file(tmp_path):
    raw, errors = load_raw(str(tmp_path / "nope.json"))
    assert raw is None
    assert any("not found" in e.lower() for e in errors)


def test_load_raw_reports_malformed_json(tmp_path):
    path = tmp_path / "rules.json"
    path.write_text("{ not json", encoding="utf-8")
    raw, errors = load_raw(str(path))
    assert raw is None
    assert errors


def test_load_rules_loads_core_by_default():
    criteria, errors = load_rules()
    assert errors == []
    assert any(c.identifier == "em-dash" for c in criteria)


def test_load_rules_merges_project_file(tmp_path):
    path = write(tmp_path, "rules.json", {
        "picassoRulesVersion": RULES_VERSION,
        "rules": [{
            "identifier": "no-lorem",
            "title": "No lorem ipsum",
            "statement": "Copy must not contain placeholder latin.",
            "level": "must-not",
            "category": "content",
            "verification": "automated",
            "message": "Placeholder latin in shipped copy.",
            "check": {"scheme": "regex", "kinds": ["copy"], "pattern": "lorem ipsum"},
            "examples": [
                {"outcome": "fail", "kind": "copy", "content": "lorem ipsum dolor"},
                {"outcome": "pass", "kind": "copy", "content": "real words here"},
            ],
        }],
    })
    criteria, errors = load_rules(path)
    assert errors == []
    assert any(c.identifier == "no-lorem" for c in criteria)
    assert any(c.identifier == "em-dash" for c in criteria)


def test_load_rules_disables_core_rule_from_project(tmp_path):
    path = write(tmp_path, "rules.json", {
        "picassoRulesVersion": RULES_VERSION,
        "rules": [{"identifier": "em-dash", "disabled": True}],
    })
    criteria, errors = load_rules(path)
    assert errors == []
    assert not any(c.identifier == "em-dash" for c in criteria)


def test_load_rules_falls_back_to_core_on_bad_project_file(tmp_path):
    path = tmp_path / "rules.json"
    path.write_text("{ broken", encoding="utf-8")
    criteria, errors = load_rules(str(path))
    assert errors
    assert any(c.identifier == "em-dash" for c in criteria)


def test_load_rules_rejects_unknown_version(tmp_path):
    path = write(tmp_path, "rules.json", {"picassoRulesVersion": "99", "rules": []})
    criteria, errors = load_rules(path)
    assert any("version" in e.lower() for e in errors)
    assert any(c.identifier == "em-dash" for c in criteria)


def test_find_project_rules_finds_sibling(tmp_path):
    (tmp_path / "rules.json").write_text("{}", encoding="utf-8")
    target = tmp_path / "tokens.css"
    target.write_text(":root{}", encoding="utf-8")
    assert find_project_rules(str(target)) == str(tmp_path / "rules.json")


def test_find_project_rules_walks_up_from_subdirectory(tmp_path):
    (tmp_path / "rules.json").write_text("{}", encoding="utf-8")
    demo = tmp_path / "demo"
    demo.mkdir()
    target = demo / "landing.html"
    target.write_text("<p>hi</p>", encoding="utf-8")
    assert find_project_rules(str(target)) == str(tmp_path / "rules.json")


def test_find_project_rules_returns_none_when_absent(tmp_path):
    target = tmp_path / "a.css"
    target.write_text(":root{}", encoding="utf-8")
    assert find_project_rules(str(target)) is None
