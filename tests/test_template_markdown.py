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
    # Prose ban lists were replaced by rendered rule blocks (Task 9); the
    # markers must be present and well-formed pairs, not the old inline prose.
    for target in ("color", "typography", "hero", "global", "manual"):
        assert f"<!-- picasso:rules:{target}:start -->" in text
        assert f"<!-- picasso:rules:{target}:end -->" in text

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

def test_design_md_carries_static_prose_above_the_typography_and_hero_blocks():
    # This prose sits outside the managed markers, so a render never
    # touches it; it is the only guidance for a section a fresh scaffold
    # ships no automated rule for (Section 4 verified this way for years).
    text = (TPL / "design.md").read_text()
    typography_prose, typography_marker, _rest = text.partition(
        "<!-- picasso:rules:typography:start -->")
    assert "Banned Fonts" in typography_prose
    hero_prose, hero_marker, _rest = text.partition(
        "<!-- picasso:rules:hero:start -->")
    assert "Banned:" in hero_prose
    assert "fake product UI" in hero_prose
