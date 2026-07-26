---
name: tokens-and-system
description: Use when authoring or editing tokens.css and design.md in a picasso project. Defines the token taxonomy, the source-of-truth discipline, and the 9-section design.md format.
---

# Tokens and system

`tokens.css` is the single source of truth. Everything else references `var(--...)`; no value is improvised elsewhere.

## Token taxonomy (Astryx-style)
Color (roles, not raw names), Typography (families, scale, weights, tracking, leading), Spacing, Size (containers; tap target at least 44px), Shape (radii), Elevation (shadows), Motion (durations, named easings). One deliberate accent. Off-black text, never pure black. Support light and dark via `prefers-color-scheme`.

## Locked-token discipline
Define every color, font, space, radius, shadow, and duration as a `:root` custom property, referenced by `var()` everywhere. Inline raw hex or px is a defect the linter flags.

## design.md (9-section format)
0. Aesthetic in one line. Config (the three dials). 1. Visual theme. 2. Color palette and roles (name, token, role, rationale; Banned Colors). 3. Typography (families, scale; Banned Fonts). 4. Component stylings (buttons, cards, inputs, nav, loaders, empty, error; eight states each; a `Not for:` line per component naming the alternative). 5. Hero or signature (fits viewport; banned: fake UI, invented metrics, version stamps). 6. Layout (grid-first, contained max-width). 7. Responsive (named breakpoints; test 375, 768, 1440). 8. Motion. 9. Anti-patterns (banned). Each visual section carries its own inline Banned subsection.

## Precedence
If `tokens.css` or `design.md` already exist, they govern. Extend them; do not silently contradict them.
