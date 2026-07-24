from pathlib import Path
from picasso_engine.frontmatter import parse_frontmatter

CMD = Path(__file__).resolve().parent.parent / "commands"
SCRIPTS = Path(__file__).resolve().parent.parent / "scripts"

def test_init_and_review_exist_with_description():
    for name in ("init.md", "review.md"):
        text = (CMD / name).read_text()
        fm = parse_frontmatter(text)
        assert fm.get("description"), f"{name} needs a description"

def test_init_references_existing_scripts():
    text = (CMD / "init.md").read_text()
    assert "picasso_scaffold.py" in text and (SCRIPTS / "picasso_scaffold.py").is_file()
    assert "picasso_review.py" in text and (SCRIPTS / "picasso_review.py").is_file()

def test_review_references_review_script():
    text = (CMD / "review.md").read_text()
    assert "picasso_review.py" in text

def test_init_review_no_dashes():
    for name in ("init.md", "review.md"):
        text = (CMD / name).read_text()
        assert "—" not in text and "–" not in text

EXPECTED_COMMANDS = {"init.md", "review.md", "brandbook.md", "system.md", "tokens.md", "demo.md"}

def test_all_six_commands_present_valid_and_dashfree():
    found = {p.name for p in CMD.glob("*.md")}
    assert EXPECTED_COMMANDS <= found, f"missing: {EXPECTED_COMMANDS - found}"
    for name in EXPECTED_COMMANDS:
        text = (CMD / name).read_text()
        assert parse_frontmatter(text).get("description"), f"{name} needs a description"
        assert "—" not in text and "–" not in text, f"{name} has a dash"

def test_alacarte_commands_run_review():
    for name in ("brandbook.md", "system.md", "tokens.md", "demo.md"):
        assert "picasso_review.py" in (CMD / name).read_text()
