---
name: accessibility
description: Use for any UI or component work in a picasso project. Encodes the WCAG AA bar picasso enforces, and how to satisfy the contrast and structural a11y checks.
---

# Accessibility

Every generated component and page meets WCAG AA. This is not a later pass; it is how the markup and tokens are chosen in the first place.

## Contrast (AA)
Body text and UI text meet 4.5:1 against their background; large text (about 24px or 18.66px bold) and non-text UI meet 3:1. The review computes ratios for the conventional token pairs (text/bg, text/surface, text-muted/bg, accent-contrast/accent). If a pair fails, adjust the token, not the markup.

## Focus
Every interactive element has a visible focus state. Never remove an outline without a replacement: use `:focus-visible` with a `box-shadow` ring (`var(--focus-ring)`). The `focus-removed` rule flags a bare `outline: none`.

## Keyboard
Everything usable with a mouse is usable with a keyboard. Prefer semantic elements (`button`, `a`, `input`, `select`). A clickable `div` or `span` needs a `role`, `tabindex`, and key handlers; the `clickable-nonsemantic` rule flags the ones without a role.

## Semantics and ARIA
Use headings in order, `label`/`for` on every control, `alt` on every image (empty `alt=""` when decorative; the `img-alt` rule flags a missing one), and roles only to fill gaps semantics cannot (`role="dialog"` + `aria-modal` on a modal, `aria-current` on the active nav link, `aria-invalid` on a bad field).

## Motion
Honor `prefers-reduced-motion: reduce` by disabling non-essential animation. Animate transform and opacity only (see the motion skill).

## Hit targets
Interactive controls are at least `var(--size-tap)` (44px) in the smallest dimension.
