---
name: components
description: Use when authoring or editing components.css and composing UI from it. Defines the reusable component layer, its class conventions, and how demos and design_system.html consume it.
---

# Components

`components.css` is the reusable component layer. It sits between `tokens.css` (values) and the pages (composition). Pages and demos import both files and use the classes; they never re-declare component styles.

## Rules
- Every value is a `var(--...)` from `tokens.css`. No raw hex, px, or color names.
- Classes are semantic and stack-agnostic: `.btn`, `.field`, `.input`, `.select`, `.textarea`, `.table`, `.badge`, `.card`, `.panel`, `.modal` (+ `.scrim`), `.nav`, `.tabs`, `.alert`, `.skeleton`, `.empty-state`, `.error-state`.
- Variants use a modifier suffix: `.btn--ghost`, `.btn--danger`, `.alert--success`. State uses attributes or `is-` classes: `[aria-current]`, `[aria-selected]`, `.is-invalid`.
- Every interactive component ships accessible by default: semantic element, `:focus-visible` ring via `var(--focus-ring)`, 44px minimum tap target, and `prefers-reduced-motion` handling on anything animated. Follow the accessibility skill.

## Consumption
Demos and `design_system.html` import `tokens.css` then `components.css`, and compose real classes. If a page needs a one-off layout rule (a page grid, a hero container), keep it in that page's `<style>`; anything reusable belongs in `components.css`.

## Precedence
If `components.css` already exists, it governs. Extend it; do not silently restyle a class other pages depend on.
