import json
import subprocess
import sys
from pathlib import Path
import picasso_scaffold as S
import picasso_review as R
from picasso_engine.kinds import kind_for
from picasso_engine.rules import PLUGIN_VERSION, stamp_for

TEMPLATES = Path(__file__).resolve().parent.parent / "templates"
SCAFFOLD_SCRIPT = Path(__file__).resolve().parent.parent / "scripts" / "picasso_scaffold.py"

def test_scaffold_copies_all_templates(tmp_path):
    written = S.scaffold(str(tmp_path), "design-system", str(TEMPLATES))
    base = tmp_path / "design-system"
    for rel in S.TEMPLATE_FILES:
        assert (base / rel).is_file(), f"missing {rel}"
    assert "demo/landing.html" in written

def test_scaffold_skips_existing_without_force(tmp_path):
    base = tmp_path / "design-system"
    (base).mkdir()
    (base / "tokens.css").write_text("/* mine */")
    written = S.scaffold(str(tmp_path), "design-system", str(TEMPLATES))
    assert "tokens.css" not in written
    assert (base / "tokens.css").read_text() == "/* mine */"

def test_scaffold_force_overwrites(tmp_path):
    base = tmp_path / "design-system"
    base.mkdir()
    (base / "tokens.css").write_text("/* mine */")
    written = S.scaffold(str(tmp_path), "design-system", str(TEMPLATES), force=True)
    assert "tokens.css" in written
    assert (base / "tokens.css").read_text() != "/* mine */"

def test_wire_claude_md_idempotent(tmp_path):
    p1 = S.wire_claude_md(str(tmp_path), "design-system")
    first = Path(p1).read_text()
    S.wire_claude_md(str(tmp_path), "design-system")
    second = Path(p1).read_text()
    assert first == second
    assert "design-system/design-instructions.md" in first

def test_instructions_block_names_folder():
    body = S.instructions_block("brand")
    assert "brand/design-instructions.md" in body
    assert "brand/tokens.css" in body

def test_scaffolded_project_passes_its_own_review(tmp_path):
    S.scaffold(str(tmp_path), "design-system", str(TEMPLATES))
    base = tmp_path / "design-system"
    results = R.review_paths([str(base)], str(base / "tokens.css"))
    assert results == [], f"fresh scaffold should be slop-free, got: {results}"

def test_scaffolded_design_md_review_by_hand_section_is_not_empty(tmp_path):
    S.scaffold(str(tmp_path), "design-system", str(TEMPLATES))
    text = (tmp_path / "design-system" / "design.md").read_text(encoding="utf-8")
    _before, _marker, after = text.partition("<!-- picasso:rules:manual:start -->")
    manual_block, _marker, _rest = after.partition("<!-- picasso:rules:manual:end -->")
    assert "No rules recorded" not in manual_block
    assert "hero-fits-viewport" in manual_block

def test_wire_claude_md_preserves_existing_content(tmp_path):
    (tmp_path / "CLAUDE.md").write_text("# My project\n\nExisting notes.\n")
    S.wire_claude_md(str(tmp_path), "design-system")
    text = (tmp_path / "CLAUDE.md").read_text()
    assert "Existing notes." in text
    assert "design-system/design-instructions.md" in text

def test_scaffold_includes_new_artifacts_not_styleguide():
    assert "components.css" in S.TEMPLATE_FILES
    assert "design_system.html" in S.TEMPLATE_FILES
    assert "styleguide.html" not in S.TEMPLATE_FILES

def test_wire_gitignore_adds_picasso_dir_idempotently(tmp_path):
    p = S.wire_gitignore(str(tmp_path), "design-system")
    from pathlib import Path
    first = Path(p).read_text()
    S.wire_gitignore(str(tmp_path), "design-system")
    second = Path(p).read_text()
    assert first == second
    assert "design-system/.picasso/" in first

def test_wire_gitignore_preserves_existing(tmp_path):
    from pathlib import Path
    (tmp_path / ".gitignore").write_text("node_modules/\n")
    S.wire_gitignore(str(tmp_path), "design-system")
    text = (tmp_path / ".gitignore").read_text()
    assert "node_modules/" in text
    assert "design-system/.picasso/" in text

def test_scaffold_writes_a_project_rules_file(tmp_path):
    S.scaffold(str(tmp_path), "design-system", str(TEMPLATES))
    path = tmp_path / "design-system" / "rules.json"
    assert path.is_file()
    raw = json.loads(path.read_text(encoding="utf-8"))
    assert raw["picassoRulesVersion"] == "1"
    assert raw["rules"] == []

def test_scaffold_reports_the_rules_file_as_written(tmp_path):
    written = S.scaffold(str(tmp_path), "design-system", str(TEMPLATES))
    assert "rules.json" in written

def test_scaffold_does_not_clobber_existing_rules(tmp_path):
    folder = tmp_path / "design-system"
    folder.mkdir(parents=True)
    (folder / "rules.json").write_text(
        json.dumps({"picassoRulesVersion": "1",
                    "rules": [{"identifier": "kept", "disabled": True}]}),
        encoding="utf-8")
    S.scaffold(str(tmp_path), "design-system", str(TEMPLATES))
    raw = json.loads((folder / "rules.json").read_text(encoding="utf-8"))
    assert raw["rules"][0]["identifier"] == "kept"

def test_scaffold_force_overwrites_rules(tmp_path):
    folder = tmp_path / "design-system"
    folder.mkdir(parents=True)
    (folder / "rules.json").write_text(
        json.dumps({"picassoRulesVersion": "1",
                    "rules": [{"identifier": "kept", "disabled": True}]}),
        encoding="utf-8")
    S.scaffold(str(tmp_path), "design-system", str(TEMPLATES), force=True)
    raw = json.loads((folder / "rules.json").read_text(encoding="utf-8"))
    assert raw["rules"] == []

def test_scaffold_stamps_every_generated_artifact(tmp_path):
    S.scaffold(str(tmp_path), "design-system", str(TEMPLATES))
    base = tmp_path / "design-system"
    for rel in S.TEMPLATE_FILES:
        path = base / rel
        kind = kind_for(str(path))
        expected = stamp_for(kind)
        last_line = path.read_text(encoding="utf-8").rstrip("\n").splitlines()[-1]
        assert last_line == expected, f"{rel}: expected last line {expected!r}, got {last_line!r}"

def test_scaffold_force_does_not_duplicate_stamps(tmp_path):
    S.scaffold(str(tmp_path), "design-system", str(TEMPLATES))
    S.scaffold(str(tmp_path), "design-system", str(TEMPLATES), force=True)
    base = tmp_path / "design-system"
    for rel in S.TEMPLATE_FILES:
        content = (base / rel).read_text(encoding="utf-8")
        # Track PLUGIN_VERSION rather than a literal: this test is about the
        # stamp not being written twice, not about which version wrote it.
        assert content.count(f"picasso {PLUGIN_VERSION}") == 1, \
            f"{rel} has a duplicated stamp"

def test_render_design_md_updates_stale_blocks_in_place(tmp_path):
    S.scaffold(str(tmp_path), "design-system", str(TEMPLATES))
    base = tmp_path / "design-system"
    (base / "rules.json").write_text(json.dumps({
        "picassoRulesVersion": "1",
        "rules": [{"identifier": "no-neon", "title": "No neon accents",
                   "statement": "Accent colors must not be neon.",
                   "level": "must-not", "category": "visual-design",
                   "verification": "automated", "target": "color",
                   "message": "Neon accent color.",
                   "check": {"scheme": "regex", "kinds": ["css"], "pattern": "neon"},
                   "examples": [
                       {"outcome": "fail", "kind": "css", "content": ".x{color:neon;}"},
                       {"outcome": "pass", "kind": "css", "content": ".x{color:blue;}"},
                   ]}],
    }), encoding="utf-8")
    changed = S.render_design_md(str(base / "design.md"))
    assert changed is True
    text = (base / "design.md").read_text(encoding="utf-8")
    assert "no-neon" in text

def test_render_design_md_preserves_content_outside_managed_blocks(tmp_path):
    S.scaffold(str(tmp_path), "design-system", str(TEMPLATES))
    base = tmp_path / "design-system"
    design_md = base / "design.md"
    text = design_md.read_text(encoding="utf-8")
    hand_written = "\n\nA hand-written closing note that must survive.\n"
    design_md.write_text(text + hand_written, encoding="utf-8")
    S.render_design_md(str(design_md))
    assert hand_written.strip() in design_md.read_text(encoding="utf-8")

def test_render_design_md_does_not_overwrite_static_prose_above_markers(tmp_path):
    S.scaffold(str(tmp_path), "design-system", str(TEMPLATES))
    base = tmp_path / "design-system"
    design_md = base / "design.md"
    text = design_md.read_text(encoding="utf-8")
    edited = text.replace(
        "**Banned Fonts:** reflexive Inter default without reason; "
        "random serif word inside a sans headline.",
        "**Banned Fonts:** a hand-edited project-specific ban.")
    design_md.write_text(edited, encoding="utf-8")
    S.render_design_md(str(design_md))
    assert "a hand-edited project-specific ban" in design_md.read_text(encoding="utf-8")

def test_render_flag_updates_design_md_and_touches_nothing_else(tmp_path):
    S.scaffold(str(tmp_path), "design-system", str(TEMPLATES))
    base = tmp_path / "design-system"
    (base / "rules.json").write_text(json.dumps({
        "picassoRulesVersion": "1",
        "rules": [{"identifier": "no-neon", "title": "No neon accents",
                   "statement": "Accent colors must not be neon.",
                   "level": "must-not", "category": "visual-design",
                   "verification": "automated", "target": "color",
                   "message": "Neon accent color.",
                   "check": {"scheme": "regex", "kinds": ["css"], "pattern": "neon"},
                   "examples": [
                       {"outcome": "fail", "kind": "css", "content": ".x{color:neon;}"},
                       {"outcome": "pass", "kind": "css", "content": ".x{color:blue;}"},
                   ]}],
    }), encoding="utf-8")
    claude_md_before = None
    proc = subprocess.run(
        [sys.executable, str(SCAFFOLD_SCRIPT), "--project", str(tmp_path),
         "--dir", "design-system", "--render"],
        text=True, capture_output=True)
    assert proc.returncode == 0
    assert "re-rendered" in proc.stdout.lower()
    assert "no-neon" in (base / "design.md").read_text(encoding="utf-8")
    assert not (tmp_path / "CLAUDE.md").is_file()
    raw = json.loads((base / "rules.json").read_text(encoding="utf-8"))
    assert len(raw["rules"]) == 1  # unchanged, still just the project's own rule

def test_render_flag_without_templates_does_not_error(tmp_path):
    S.scaffold(str(tmp_path), "design-system", str(TEMPLATES))
    proc = subprocess.run(
        [sys.executable, str(SCAFFOLD_SCRIPT), "--project", str(tmp_path),
         "--dir", "design-system", "--render"],
        text=True, capture_output=True)
    assert proc.returncode == 0

def test_render_flag_reports_missing_design_md(tmp_path):
    proc = subprocess.run(
        [sys.executable, str(SCAFFOLD_SCRIPT), "--project", str(tmp_path),
         "--dir", "design-system", "--render"],
        text=True, capture_output=True)
    assert proc.returncode != 0
