import pytest
from picasso_engine.rules import (
    Criterion, validate_rules, criteria_from, severity_for, RULES_VERSION,
)


def wrap(*rules):
    return {"picassoRulesVersion": RULES_VERSION, "rules": list(rules)}


def good(**over):
    rule = {
        "identifier": "no-foo",
        "title": "No foo",
        "statement": "Content must not contain foo.",
        "level": "must-not",
        "category": "content",
        "verification": "automated",
        "message": "Found foo.",
        "check": {"scheme": "regex", "kinds": ["copy"], "pattern": "foo"},
        "examples": [
            {"outcome": "fail", "kind": "copy", "content": "foo"},
            {"outcome": "pass", "kind": "copy", "content": "bar"},
        ],
    }
    rule.update(over)
    return rule


def test_valid_rule_has_no_errors():
    assert validate_rules(wrap(good())) == []


def test_severity_derives_from_level():
    assert severity_for("must") == "warn"
    assert severity_for("must-not") == "warn"
    assert severity_for("should") == "info"
    assert severity_for("should-not") == "info"


def test_rejects_missing_required_field():
    rule = good()
    del rule["statement"]
    errors = validate_rules(wrap(rule))
    assert any("statement" in e for e in errors)


def test_rejects_unknown_field():
    errors = validate_rules(wrap(good(colour="blue")))
    assert any("colour" in e for e in errors)


def test_rejects_bad_level():
    errors = validate_rules(wrap(good(level="mandatory")))
    assert any("level" in e for e in errors)


def test_rejects_bad_category():
    errors = validate_rules(wrap(good(category="vibes")))
    assert any("category" in e for e in errors)


def test_rejects_bad_verification():
    errors = validate_rules(wrap(good(verification="eyeball")))
    assert any("verification" in e for e in errors)


def test_rejects_check_on_manual_rule():
    rule = good(verification="manual")
    errors = validate_rules(wrap(rule))
    assert any("check" in e for e in errors)


def test_manual_rule_without_check_is_valid():
    rule = good(verification="manual")
    del rule["check"]
    del rule["message"]
    del rule["examples"]
    assert validate_rules(wrap(rule)) == []


def test_rejects_automated_rule_without_check():
    rule = good()
    del rule["check"]
    errors = validate_rules(wrap(rule))
    assert any("check" in e for e in errors)


def test_rejects_automated_rule_without_message():
    rule = good()
    del rule["message"]
    errors = validate_rules(wrap(rule))
    assert any("message" in e for e in errors)


def test_rejects_uncompilable_pattern():
    errors = validate_rules(wrap(good(check={
        "scheme": "regex", "kinds": ["copy"], "pattern": "("})))
    assert any("pattern" in e for e in errors)


def test_rejects_unknown_scheme():
    errors = validate_rules(wrap(good(check={"scheme": "telepathy"})))
    assert any("scheme" in e for e in errors)


def test_rejects_unknown_builtin_name():
    errors = validate_rules(wrap(good(
        check={"scheme": "builtin", "name": "does_not_exist"})))
    assert any("builtin" in e for e in errors)


def test_rejects_duplicate_identifier():
    errors = validate_rules(wrap(good(), good()))
    assert any("duplicate" in e.lower() for e in errors)


def test_rejects_rationale_restating_statement():
    errors = validate_rules(wrap(good(
        statement="Content must not contain foo.",
        rationale="content must not contain foo",
    )))
    assert any("rationale" in e for e in errors)


def test_rejects_missing_pass_example():
    errors = validate_rules(wrap(good(examples=[
        {"outcome": "fail", "kind": "copy", "content": "foo"}])))
    assert any("example" in e for e in errors)


def test_rejects_missing_fail_example():
    errors = validate_rules(wrap(good(examples=[
        {"outcome": "pass", "kind": "copy", "content": "bar"}])))
    assert any("example" in e for e in errors)


def test_rejects_disabled_when_not_allowed():
    errors = validate_rules(wrap({"identifier": "no-foo", "disabled": True}))
    assert any("disabled" in e for e in errors)


def test_allows_disabled_stub_in_project_file():
    raw = wrap({"identifier": "no-foo", "disabled": True})
    assert validate_rules(raw, allow_disabled=True) == []


def test_rejects_unknown_version():
    raw = {"picassoRulesVersion": "99", "rules": [good()]}
    errors = validate_rules(raw)
    assert any("version" in e.lower() for e in errors)


def test_rejects_missing_rules_key():
    errors = validate_rules({"picassoRulesVersion": RULES_VERSION})
    assert any("rules" in e for e in errors)


def test_criteria_from_builds_criterion_objects():
    (crit,) = criteria_from(wrap(good()))
    assert isinstance(crit, Criterion)
    assert crit.identifier == "no-foo"
    assert crit.checks == [{"scheme": "regex", "kinds": ["copy"], "pattern": "foo"}]


def test_rejects_token_pair_mixed_with_another_scheme():
    rule = good(check=[
        {"scheme": "token-pair", "pairs": [["color-text", "color-bg"]]},
        {"scheme": "regex", "kinds": ["copy"], "pattern": "foo"},
    ])
    errors = validate_rules(wrap(rule))
    assert any("token-pair" in e for e in errors)


def test_check_array_normalizes_to_checks_list():
    rule = good(check=[
        {"scheme": "regex", "kinds": ["copy"], "pattern": "foo"},
        {"scheme": "regex", "kinds": ["html"], "pattern": "foo"},
    ])
    (crit,) = criteria_from(wrap(rule))
    assert len(crit.checks) == 2
