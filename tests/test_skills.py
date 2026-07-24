from pathlib import Path
from picasso_engine.frontmatter import parse_frontmatter

SKILLS = Path(__file__).resolve().parent.parent / "skills"

def _skill(name):
    return (SKILLS / name / "SKILL.md").read_text()

def test_present_skills_have_matching_name_and_description():
    for name in ("taste", "brand", "tokens-and-system"):
        fm = parse_frontmatter(_skill(name))
        assert fm.get("name") == name
        assert fm.get("description")

def test_present_skills_are_dashfree():
    for name in ("taste", "brand", "tokens-and-system"):
        text = _skill(name)
        assert "—" not in text and "–" not in text

def test_taste_covers_dials_and_locks():
    text = _skill("taste")
    for marker in ("DESIGN_VARIANCE", "MOTION_INTENSITY", "VISUAL_DENSITY", "Design Read"):
        assert marker in text

def test_brand_covers_voice_and_values():
    text = _skill("brand").lower()
    for marker in ("voice essence", "values", "things we never say"):
        assert marker in text

def test_tokens_skill_covers_taxonomy_and_precedence():
    text = _skill("tokens-and-system").lower()
    for marker in ("var(--", "precedence", "9-section", "source of truth"):
        assert marker in text

ALL_SKILLS = ("taste", "brand", "tokens-and-system", "motion", "unslop-copy", "accessibility", "components")

def test_all_five_skills_present_valid_and_dashfree():
    for name in ALL_SKILLS:
        text = _skill(name)
        fm = parse_frontmatter(text)
        assert fm.get("name") == name, f"{name} frontmatter name mismatch"
        assert fm.get("description"), f"{name} needs a description"
        assert "—" not in text and "–" not in text, f"{name} has a dash"

def test_motion_covers_transform_and_reduced_motion():
    text = _skill("motion").lower()
    for marker in ("transform", "opacity", "prefers-reduced-motion", "motivated"):
        assert marker in text

def test_unslop_covers_three_levels():
    text = _skill("unslop-copy")
    for marker in ("Level 1", "Level 2", "Level 3", "Outline test"):
        assert marker in text

def test_accessibility_skill_valid_and_dashfree():
    text = _skill("accessibility")
    fm = parse_frontmatter(text)
    assert fm.get("name") == "accessibility"
    assert fm.get("description")
    assert "—" not in text and "–" not in text

def test_accessibility_covers_core_topics():
    text = _skill("accessibility").lower()
    for marker in ("wcag", "contrast", "focus-visible", "keyboard", "aria", "reduced-motion"):
        assert marker in text

def test_components_skill_valid_and_dashfree():
    text = _skill("components")
    fm = parse_frontmatter(text)
    assert fm.get("name") == "components"
    assert fm.get("description")
    assert "—" not in text and "–" not in text

def test_components_skill_covers_layer_rules():
    text = _skill("components").lower()
    for marker in ("components.css", "var(--", "semantic", "focus-visible"):
        assert marker in text
