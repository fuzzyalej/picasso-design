from pathlib import Path
import picasso_scaffold as S
import picasso_review as R

TEMPLATES = Path(__file__).resolve().parent.parent / "templates"

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
