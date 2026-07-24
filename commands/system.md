---
description: Generate or refresh design.md (theme, color roles, type, components, layout, motion, banned anti-patterns).
---

Load the picasso `taste`, `tokens-and-system`, `accessibility`, and `motion` skills.

Determine the design-system folder `<folder>`: use `design-system` by default, or the folder named in the picasso block of `CLAUDE.md` if a different one was chosen at init.

Fill `<folder>/design.md`: aesthetic in one line, the three resolved dials, color roles as tokens, typography, component stylings with the eight interaction states, hero and signature rules, layout, responsive breakpoints, motion doctrine, and the banned anti-patterns list. Reference `var(--...)` from `tokens.css`; never restate raw values.

Add an accessibility section (the AA contrast bar, focus, keyboard, semantics, reduced-motion) and a component inventory listing the classes in `components.css`.

When done, run `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/picasso_review.py" <folder>/design.md`.
