# Working with this project's design system

This project has a design system. Follow it for all UI and copy work.

**Source of truth and precedence (highest first):**
1. `design-system/tokens.css`: every color, font, space, radius, shadow, motion value. Reference via `var(--...)`. Never inline raw values.
2. `design-system/design.md`: the visual system, rules, and banned anti-patterns.
3. `design-system/brandbook.md`: voice, tone, values, visual identity.

When these files exist, they override any inference. Do not improvise values that contradict them.

**Before building UI:** state a one-line Design Read (page kind, audience, vibe) and honor the dials in `design.md`.

**Every interactive component** ships eight states: default, hover, focus-visible, active, disabled, loading, error, success. Every screen handles loading (skeleton matching layout), empty, and error states.

**Copy:** no em-dashes, no fabricated metrics or testimonials, no filler. Run the unslop discipline: fix mechanics, drop cliches, then break machine-shaped structure.

**Review:** run `picasso:review` to audit screens and copy against these files.

**Visual review:** open `design-system/design_system.html` and `design-system/brandbook.html` in a browser.

Compose UI from `components.css` (import it after `tokens.css`); do not re-declare
component styles inline. See the whole system in `design_system.html`. All UI must
meet WCAG AA: real focus states, semantic markup, image alt text, and contrast that
passes the review.
