"""A builtin check declares which kinds it applies to in the JSON, so
rules/core.json alone tells you when a rule runs — no reading Python."""
import pytest

from picasso_engine.rules import RULES_VERSION, load_rules, validate_rules
from picasso_engine.schemes import run_check

PURPLE_CSS = ".h{background:linear-gradient(90deg,indigo,purple);}"


def wrap(rule):
    return {"picassoRulesVersion": RULES_VERSION, "rules": [rule]}


def builtin_rule(**over):
    rule = {
        "identifier": "no-foo",
        "title": "No foo",
        "statement": "Content must not contain foo.",
        "level": "must-not",
        "category": "content",
        "verification": "automated",
        "message": "Found foo.",
        "check": {"scheme": "builtin", "name": "purple_gradient",
                  "kinds": ["html", "css"]},
        "examples": [
            {"outcome": "fail", "kind": "css", "content": PURPLE_CSS},
            {"outcome": "pass", "kind": "css", "content": ".h{color:var(--a);}"},
        ],
    }
    rule.update(over)
    return rule


def test_builtin_check_runs_for_a_declared_kind():
    check = {"scheme": "builtin", "name": "purple_gradient", "kinds": ["css"]}
    assert run_check(check, PURPLE_CSS, "css")


def test_builtin_check_is_inert_for_an_undeclared_kind():
    """The declared kinds gate the builtin, not a guard inside its body."""
    check = {"scheme": "builtin", "name": "purple_gradient", "kinds": ["html"]}
    assert run_check(check, PURPLE_CSS, "css") == []


def test_builtin_check_without_kinds_matches_nothing():
    """Same contract as the regex scheme: absent kinds means no kinds."""
    check = {"scheme": "builtin", "name": "purple_gradient"}
    assert run_check(check, PURPLE_CSS, "css") == []


def test_validate_rejects_a_builtin_check_without_kinds():
    rule = builtin_rule()
    del rule["check"]["kinds"]
    errors = validate_rules(wrap(rule))
    assert any("kinds" in e for e in errors)


def test_validate_rejects_a_builtin_check_with_an_unknown_kind():
    rule = builtin_rule()
    rule["check"]["kinds"] = ["prose"]
    errors = validate_rules(wrap(rule))
    assert any("kinds" in e for e in errors)


def test_validate_accepts_a_builtin_check_with_kinds():
    assert validate_rules(wrap(builtin_rule())) == []


CORE, _ERRORS = load_rules()
BUILTIN_CHECKS = [
    (criterion.identifier, check)
    for criterion in CORE
    for check in criterion.checks
    if check.get("scheme") == "builtin"
]


def test_core_has_builtin_checks_to_audit():
    assert len(BUILTIN_CHECKS) >= 7


@pytest.mark.parametrize("identifier,check", BUILTIN_CHECKS,
                         ids=[i for i, _ in BUILTIN_CHECKS])
def test_every_shipped_builtin_check_declares_its_kinds(identifier, check):
    kinds = check.get("kinds")
    assert kinds, f"{identifier}: builtin check does not declare kinds"
    assert set(kinds) <= {"html", "css", "copy"}, f"{identifier}: bad kinds {kinds}"
