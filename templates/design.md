# Design System

## 0. Aesthetic in one line
> One poetic descriptor that anchors intent (e.g. "a quiet white gallery wall with one blue element").

## Configuration
These dials are inferred from a Design Read, not asked. Baseline shown; override in conversation, never by improvising values elsewhere.

| Dial | Range | Default | Meaning |
| --- | --- | --- | --- |
| DESIGN_VARIANCE | 1..10 | 8 | symmetry vs. surprise |
| MOTION_INTENSITY | 1..10 | 6 | static vs. cinematic |
| VISUAL_DENSITY | 1..10 | 4 | airy vs. dense |

## 1. Visual Theme and Atmosphere
One paragraph describing the feel.

## 2. Color Palette and Roles
Each line: name, value token, role, rationale. All values live in `tokens.css`.
- Accent: `var(--color-accent)`, primary action.
**Banned Colors:** pure black, indigo/purple gradients, oversaturated accents.

## 3. Typography Rules
Families, scale, tracking, leading (all tokens).
**Banned Fonts:** reflexive Inter default without reason; random serif word inside a sans headline.

## 4. Component Stylings
Buttons, cards, inputs, nav, loaders, empty, error. One line each. Every interactive component ships 8 states.

## 5. Hero / Signature Section
Fits in viewport, at most 2 headline lines, subtext under 20 words.
**Banned:** fake product UI, invented metrics, version stamps, scroll cues.

## 6. Layout Principles
Grid-first, contained max-width, deliberate whitespace.

## 7. Responsive Rules
Named breakpoints, tested at 375, 768, 1440.

## 8. Motion and Interaction
Motion must be motivated. Animate transform and opacity only. Respect prefers-reduced-motion.

## 9. Anti-Patterns (Banned)
- Three equal rounded cards as the only feature layout.
- Eyebrows above every section.
- Section-number labels and middle-dot separators everywhere.
- Fabricated testimonials, logos, or metrics.
