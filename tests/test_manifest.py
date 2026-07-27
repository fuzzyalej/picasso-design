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


def test_manifest_version_matches_the_engine_stamp():
    # rules.py's PLUGIN_VERSION is written into every generated artifact by
    # stamp_for(), so a drifting manifest silently mislabels output.
    import json
    from pathlib import Path
    from picasso_engine.rules import PLUGIN_VERSION
    manifest = Path(__file__).resolve().parent.parent / ".claude-plugin" / "plugin.json"
    assert json.loads(manifest.read_text())["version"] == PLUGIN_VERSION
