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
<!-- picasso:rules:color:start -->
<!-- picasso:rules:color:end -->

## 3. Typography Rules
Families, scale, tracking, leading (all tokens).
**Banned Fonts:** reflexive Inter default without reason; random serif word inside a sans headline.
<!-- picasso:rules:typography:start -->
<!-- picasso:rules:typography:end -->

## 4. Component Stylings
Buttons, cards, inputs, nav, loaders, empty, error. One line each, then a
`Not for:` line naming what to use instead. Every interactive component ships 8 states.
- Button `.btn`: solid fill, one accent.
  Not for: destructive actions, use `.btn--danger`.
- Field `.field`: label, input, hint.
  Not for: read-only display, use `.table`.
- Label `.label`: input caption.
  Not for: standalone body text, use plain prose.
- Input `.input`: single-line text entry.
  Not for: long-form text, use `.textarea`.
- Select `.select`: one choice from a fixed, short list.
  Not for: free-form text, use `.input`.
- Textarea `.textarea`: multi-line text entry.
  Not for: a single value on one line, use `.input`.
- Table `.table`: tabular data, many rows of the same shape.
  Not for: single-record detail, use `.card`.
- Badge `.badge`: short status label.
  Not for: primary actions, use `.btn`.
- Card `.card`: bordered content container in a repeating grid.
  Not for: blocking confirmation, use `.modal`.
- Panel `.panel`: a settings or grouped-content section, not repeated.
  Not for: repeating list items in a grid, use `.card`.
- Scrim `.scrim`: modal backdrop.
  Not for: page background, leave unset.
- Modal `.modal`: blocking dialog.
  Not for: transient feedback, use `.alert`.
- Nav `.nav`: primary navigation links.
  Not for: in-page section switching, use `.tabs`.
- Tabs `.tabs`: in-page section switching.
  Not for: primary navigation, use `.nav`.
- Alert `.alert`: inline status message.
  Not for: blocking confirmation, use `.modal`.
- Skeleton `.skeleton`: loading placeholder.
  Not for: permanent empty content, use `.empty-state`.
- Empty state `.empty-state`: no data yet.
  Not for: a failed request, use `.error-state`.
- Error state `.error-state`: failed request.
  Not for: nothing loaded yet, use `.empty-state`.

## 5. Hero / Signature Section
Fits in viewport, at most 2 headline lines, subtext under 20 words.
**Banned:** fake product UI, invented metrics, version stamps, scroll cues.
<!-- picasso:rules:hero:start -->
<!-- picasso:rules:hero:end -->

## 6. Layout Principles
Grid-first, contained max-width, deliberate whitespace.

## 7. Responsive Rules
Named breakpoints, tested at 375, 768, 1440.

## 8. Motion and Interaction
Motion must be motivated. Animate transform and opacity only. Respect prefers-reduced-motion.

## 9. Anti-Patterns (Banned)
<!-- picasso:rules:global:start -->
<!-- picasso:rules:global:end -->

## 10. Review by hand
<!-- picasso:rules:manual:start -->
<!-- picasso:rules:manual:end -->
