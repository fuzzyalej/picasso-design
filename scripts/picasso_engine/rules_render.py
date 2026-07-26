"""Render criteria into design.md managed blocks. Pure string work."""
from picasso_engine.claude_md import extract_managed_block, upsert_managed_block

BLOCK_TARGETS = ("color", "typography", "hero", "global", "manual")

_HEADINGS = {
    "color": "Banned colors",
    "typography": "Banned fonts",
    "hero": "Banned in the hero",
    "global": "Anti-patterns (banned)",
    "manual": "Review by hand",
}

_EMPTY = "_No rules recorded for this section yet._"


def _bucket(criterion) -> str:
    """Verification mode wins over target: an untestable rule never sits in a
    list of enforced bans."""
    if criterion.verification != "automated":
        return "manual"
    return criterion.target if criterion.target in BLOCK_TARGETS else "global"


def render_block(criteria, target: str) -> str:
    selected = [c for c in criteria if _bucket(c) == target]
    lines = [f"**{_HEADINGS.get(target, target)}**", ""]
    if not selected:
        lines.append(_EMPTY)
        return "\n".join(lines)
    for criterion in selected:
        prefix = "- [ ] " if target == "manual" else "- "
        line = f"{prefix}`{criterion.identifier}` ({criterion.level}) " \
               f"{criterion.statement}"
        lines.append(line)
        if criterion.rationale:
            lines.append(f"  Why: {criterion.rationale}")
    return "\n".join(lines)


def render_all(existing: str, criteria) -> str:
    out = existing
    for target in BLOCK_TARGETS:
        out = upsert_managed_block(out, render_block(criteria, target),
                                   name=f"rules:{target}")
    return out


def stale_blocks(existing: str, criteria) -> list:
    """Names of blocks whose on-disk body differs from a fresh render."""
    stale = []
    for target in BLOCK_TARGETS:
        current = extract_managed_block(existing, name=f"rules:{target}")
        if current is None:
            continue
        if current.strip() != render_block(criteria, target).strip():
            stale.append(target)
    return stale
