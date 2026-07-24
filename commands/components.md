---
description: Generate or refresh components.css, the reusable component layer built from tokens.css.
---

Load the picasso `taste`, `tokens-and-system`, `components`, `accessibility`, and `motion` skills.

Determine the design-system folder `<folder>`: use `design-system` by default, or the folder named in the picasso block of `CLAUDE.md` if a different one was chosen at init.

Edit `<folder>/components.css` so every component reflects this project's tokens: actions, form fields, tables, badges, cards, overlays (modal plus scrim), navigation and tabs, alerts, and the loading, empty, and error states. Import `tokens.css` at the top. Reference `var(--...)` for every value; never inline raw hex or px. Every interactive component ships accessible: a visible `:focus-visible` ring, 44px tap targets, correct semantics, and reduced-motion handling.

When done, run `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/picasso_review.py" <folder>/components.css --tokens <folder>/tokens.css` and resolve anything it flags.
