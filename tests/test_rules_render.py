from picasso_engine.claude_md import upsert_managed_block
from picasso_engine.rules import Criterion
from picasso_engine.rules_render import (
    BLOCK_TARGETS, render_block, render_all, stale_blocks,
)


def crit(identifier, **over):
    values = dict(
        identifier=identifier, title=identifier.replace("-", " ").capitalize(),
        statement="S.", level="must-not", category="visual-design",
        verification="automated", message="M",
    )
    values.update(over)
    return Criterion(**values)


def skeleton():
    body = []
    for name in BLOCK_TARGETS:
        body.append(f"<!-- picasso:rules:{name}:start -->")
        body.append(f"<!-- picasso:rules:{name}:end -->")
    return "\n".join(body) + "\n"


def test_named_block_roundtrips():
    out = upsert_managed_block("", "hello", name="rules:color")
    assert "<!-- picasso:rules:color:start -->" in out
    assert "hello" in out


def test_named_blocks_do_not_collide():
    out = upsert_managed_block(skeleton(), "COLOR", name="rules:color")
    out = upsert_managed_block(out, "TYPE", name="rules:typography")
    assert "COLOR" in out and "TYPE" in out


def test_default_block_name_is_unchanged():
    out = upsert_managed_block("", "body")
    assert "<!-- picasso:start -->" in out


def test_render_block_groups_by_target():
    criteria = [crit("no-pure-black", target="color"),
                crit("no-inter", target="typography")]
    assert "no-pure-black" in render_block(criteria, "color")
    assert "no-inter" not in render_block(criteria, "color")


def test_untargeted_rule_renders_into_global():
    criteria = [crit("three-cards")]
    assert "three-cards" in render_block(criteria, "global")


def test_verification_mode_wins_over_target():
    criteria = [crit("hero-fits", target="color", verification="manual")]
    assert "hero-fits" not in render_block(criteria, "color")
    assert "hero-fits" in render_block(criteria, "manual")


def test_render_block_includes_the_rationale():
    criteria = [crit("no-pure-black", target="color",
                     rationale="Harsh on screens.")]
    assert "Harsh on screens." in render_block(criteria, "color")


def test_empty_block_renders_a_placeholder_not_a_crash():
    assert render_block([], "color").strip()


def test_render_all_is_idempotent():
    criteria = [crit("no-pure-black", target="color")]
    once = render_all(skeleton(), criteria)
    twice = render_all(once, criteria)
    assert once == twice


def test_render_all_preserves_content_outside_blocks():
    existing = "# Design System\n\n" + skeleton() + "\nHand-written tail.\n"
    out = render_all(existing, [crit("x", target="color")])
    assert "# Design System" in out
    assert "Hand-written tail." in out


def test_stale_blocks_is_empty_when_in_sync():
    criteria = [crit("no-pure-black", target="color")]
    rendered = render_all(skeleton(), criteria)
    assert stale_blocks(rendered, criteria) == []


def test_stale_blocks_names_a_diverged_block():
    criteria = [crit("no-pure-black", target="color")]
    rendered = render_all(skeleton(), criteria)
    tampered = rendered.replace("no-pure-black", "hand-edited")
    assert "color" in stale_blocks(tampered, criteria)
