---
description: Generate or refresh tokens.css, the design-system source of truth.
---

Load the picasso `taste`, `tokens-and-system`, and `accessibility` skills.

Determine the design-system folder `<folder>`: use `design-system` by default, or the folder named in the picasso block of `CLAUDE.md` if a different one was chosen at init.

Edit `<folder>/tokens.css` so every token reflects this project: one deliberate accent (never an indigo or purple default), off-black text (never pure black), a real type scale, spacing, radii, elevation, and motion, keeping the Astryx-style taxonomy. `<folder>/design_system.html` renders from these tokens; do not hardcode values in it. Keep every conventional color pair at WCAG AA (the review computes them).

When done, run `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/picasso_review.py" <folder>/tokens.css <folder>/design_system.html --tokens <folder>/tokens.css` and tell the user to open `design_system.html`.
