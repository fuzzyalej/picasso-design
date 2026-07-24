import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def test_plugin_manifest_valid():
    data = json.loads((ROOT / ".claude-plugin" / "plugin.json").read_text())
    assert data["name"] == "picasso"
    assert data["version"]
    assert data["description"]


def test_expected_components_present():
    for sub in ("commands", "skills", "scripts", "templates", "hooks"):
        assert (ROOT / sub).is_dir(), f"missing {sub}/"
    assert (ROOT / "hooks" / "hooks.json").is_file()
    assert (ROOT / "scripts" / "picasso_engine" / "slop_lint.py").is_file()
