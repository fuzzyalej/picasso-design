from pathlib import Path
from picasso_engine.slop_lint import lint

TPL = Path(__file__).resolve().parent.parent / "templates"

def test_design_md_has_nine_sections_and_dials():
    text = (TPL / "design.md").read_text()
    for n in range(0, 10):
        assert f"## {n}." in text or f"## {n} " in text or f"## {n}\n" in text
    assert "DESIGN_VARIANCE" in text
    assert "MOTION_INTENSITY" in text
    assert "VISUAL_DENSITY" in text
    assert "Banned" in text  # inline ban subsections present

def test_brandbook_md_has_core_sections():
    text = (TPL / "brandbook.md").read_text().lower()
    for section in ("values", "voice", "tone", "personality", "brand don'ts"):
        assert section in text

def test_design_instructions_reference_source_of_truth():
    text = (TPL / "design-instructions.md").read_text()
    assert "tokens.css" in text
    assert "design.md" in text
    assert "brandbook.md" in text

def test_markdown_scaffolds_not_sloppy():
    for name in ("design.md", "brandbook.md", "design-instructions.md"):
        text = (TPL / name).read_text()
        rules = {f.rule for f in lint(text, "copy")}
        assert "em-dash" not in rules, f"{name} contains em/en dash"
        assert "fake-metric" not in rules, f"{name} contains a fabricated metric"
