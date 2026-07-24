---
description: Assemble or refresh design_system.html, the single page showing brand, palette, type, values, and every component together.
---

Load the picasso `taste`, `brand`, `tokens-and-system`, `components`, and `accessibility` skills.

Determine the design-system folder `<folder>`: use `design-system` by default, or the folder named in the picasso block of `CLAUDE.md` if a different one was chosen at init.

Rebuild `<folder>/design_system.html` from the current artifacts. Import `tokens.css` then `components.css`. Show, in order: brand (mission and personality from `brandbook.md`), values, the palette as swatches, the type scale, the full component gallery composed from `components.css` classes (buttons, a form with a valid and an invalid field, a table, a modal, alerts, and the loading, empty, and error states), and a contrast section that computes each conventional token pair's ratio at runtime and marks pass or fail. Keep the page self-contained, reference only `var(--...)`, use `minmax(0, 1fr)` for grids, give every button a distinct label, and add no fabricated numbers.

When done, run `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/picasso_review.py" <folder>/design_system.html --tokens <folder>/tokens.css`, resolve anything it flags, and tell the user to open `<folder>/design_system.html`.
