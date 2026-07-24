---
description: Generate or refresh the project's brandbook (foundation, voice and tone, values, visual identity).
---

Load the picasso `taste`, `brand`, and `unslop-copy` skills.

Determine the design-system folder `<folder>`: use `design-system` by default, or the folder named in the picasso block of `CLAUDE.md` if `picasso:init` used a different one. If `<folder>/brandbook.md` does not exist, first run `picasso:init`, or scaffold with:
`python3 "${CLAUDE_PLUGIN_ROOT}/scripts/picasso_scaffold.py" --project . --dir <folder> --templates "${CLAUDE_PLUGIN_ROOT}/templates"`

State a one-line Design Read, then fill the brandbook with real, project-specific content: mission, vision, 4 to 5 one-sentence values, roughly five-word personality, positioning; voice essence, tone axes, voice do and don't, things we never say; visual identity; and a consolidated Brand Don'ts list. No fabricated facts, no em-dashes, no filler.

When done, run `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/picasso_review.py" <folder>/brandbook.md`.
