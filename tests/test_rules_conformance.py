import pytest
from picasso_engine.rules import load_rules, validate_rules, load_raw, CORE_PATH
from picasso_engine.slop_lint import findings_for
from picasso_engine.tokens import parse_tokens

CORE, LOAD_ERRORS = load_rules()
AUTOMATED = [c for c in CORE if c.verification == "automated"]

# test_every_automated_rule_has_both_example_outcomes and
# test_every_automated_rule_documents_itself duplicate checks that
# validate_rules already performs at load time (rules.py), so today they
# cannot fail against core.json. They stay in place as defence-in-depth: if
# validate_rules is ever loosened, this suite still catches an undocumented
# or unexemplified rule.


def cases():
    for criterion in AUTOMATED:
        for index, example in enumerate(criterion.examples):
            yield pytest.param(
                criterion, example,
                id=f"{criterion.identifier}-{example.get('outcome')}-{index}")


def test_core_rules_load_without_error():
    assert LOAD_ERRORS == []


def test_core_json_is_valid():
    raw, errors = load_raw(CORE_PATH)
    assert errors == []
    assert validate_rules(raw) == []


def test_core_set_is_not_empty():
    assert len(AUTOMATED) >= 11


def test_conformance_generates_a_case_per_example():
    generated = list(cases())
    total_examples = sum(len(c.examples) for c in AUTOMATED)
    assert len(generated) == total_examples
    # Floor guards against a silently-empty rule set collapsing every
    # parametrized test into a single SKIPPED placeholder.
    assert len(generated) >= 25


@pytest.mark.parametrize("criterion", AUTOMATED, ids=lambda c: c.identifier)
def test_every_automated_rule_has_both_example_outcomes(criterion):
    outcomes = {e.get("outcome") for e in criterion.examples}
    assert "fail" in outcomes, f"{criterion.identifier} has no failing example"
    assert "pass" in outcomes, f"{criterion.identifier} has no passing example"


@pytest.mark.parametrize("criterion", AUTOMATED, ids=lambda c: c.identifier)
def test_every_automated_rule_documents_itself(criterion):
    assert criterion.title
    assert criterion.statement
    assert criterion.message


@pytest.mark.parametrize("criterion,example", list(cases()))
def test_example_reproduces_its_declared_outcome(criterion, example):
    content = example["content"]
    kind = example["kind"]
    # A criterion whose check reads tokens gets them from the example itself,
    # so an example stays a single self-contained document.
    tokens = parse_tokens(content) if kind == "css" else {}
    if criterion.identifier == "component-use-cases":
        pytest.skip("needs a project directory; covered by test_schemes_use_cases.py")
    found = {f.rule for f in findings_for(criterion, content, kind, tokens)}
    if example["outcome"] == "fail":
        assert criterion.identifier in found, (
            f"{criterion.identifier}: failing example produced no finding")
    else:
        assert criterion.identifier not in found, (
            f"{criterion.identifier}: passing example produced a finding")
