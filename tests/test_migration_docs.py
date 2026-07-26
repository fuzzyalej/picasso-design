import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def read(*parts):
    with open(os.path.join(ROOT, *parts), "r", encoding="utf-8") as fh:
        return fh.read()


def test_plugin_version_is_bumped():
    manifest = json.loads(read(".claude-plugin", "plugin.json"))
    assert manifest["version"] == "0.4.0"


def test_migration_doc_records_version_one():
    text = read("docs", "migration.md")
    assert "picassoRulesVersion" in text
    assert re.search(r"\b1\b", text)


def test_architecture_documents_the_rule_layer():
    text = read("docs", "architecture.md")
    assert "rules/core.json" in text
    assert "rules.json" in text


def test_reference_lists_the_schemes():
    text = read("docs", "reference.md")
    for scheme in ("regex", "token-pair", "builtin"):
        assert scheme in text


def test_core_rules_are_stamped_with_the_format_version():
    raw = json.loads(read("rules", "core.json"))
    assert raw["picassoRulesVersion"] == "1"
