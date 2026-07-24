---
description: Generate demo screens that compose the design system's components (with loading, empty, and error states).
argument-hint: "[screen names]"
---

Load the picasso `taste`, `tokens-and-system`, `motion`, and `unslop-copy` skills.

Determine the design-system folder `<folder>`: use `design-system` by default, or the folder named in the picasso block of `CLAUDE.md` if a different one was chosen at init.

Ask the user which screens to generate if none are given in `$ARGUMENTS`; suggest a set inferred from the project and do not cap the number.

For each screen, author a self-contained HTML file in `<folder>/demo/` that imports `../tokens.css`, composes real components using only defined tokens, and includes loading (skeleton matching layout), empty, and error states plus a grid layout. These are compositions for feedback, not a mirror of real features; do not invent metrics, logos, or testimonials.

When done, run `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/picasso_review.py" <folder>/demo --tokens <folder>/tokens.css`.
