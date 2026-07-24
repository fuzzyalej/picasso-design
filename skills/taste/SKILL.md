---
name: taste
description: Use before generating or reviewing any UI in a picasso project. Establishes the Design Read, the three dials, consistency locks, and the anti-slop discipline that keeps output deliberate rather than generic.
---

# Taste

Good interfaces read as deliberate and restrained, not decorated. Before writing any UI, orient; while writing, hold the locks. The goal is one coherent system, not a sampler of effects.

## 1. Design Read (before any code)
State one line: "Reading this as a <page kind> for <audience>, with a <vibe> language, leaning <system or aesthetic>." Infer, do not interrogate. Ask at most one question, and only on genuine divergence.

## 2. The three dials
Infer these from the read and record them in `design.md`. Baseline 8 / 6 / 4.
- DESIGN_VARIANCE (1 to 10): symmetry vs. surprise.
- MOTION_INTENSITY (1 to 10): static vs. cinematic.
- VISUAL_DENSITY (1 to 10): airy vs. dense.
Signal map: minimalist 5/3/2, premium 7/6/3, playful 10/9/3, trust-first or public-sector 3/2/5. Override in conversation, never by improvising values mid-render.

## 3. Real design system vs. aesthetic
If the brief matches an official system (Material, Fluent, Carbon, Polaris, Primer, GOV.UK, USWDS), use it rather than hand-recreating its tokens. Aesthetics (editorial, bento, brutalist, glassmorphism) have no package: build natively and label borrowed inspiration in a comment. One system per project.

## 4. Consistency locks (mandatory)
One accent color page-wide. One radius scale. One theme (no section inverts light or dark arbitrarily). One copy register. One label per CTA intent. Hero fits the viewport, at most two headline lines, subtext under twenty words, at most four text elements.

## 5. Precedence
A present `tokens.css`, `design.md`, or `brandbook.md` overrides all inference. Read them first and do not contradict them.

## 6. Pre-emit self-critique
Before shipping a screen, score it 1 to 5 on Philosophy, Hierarchy, Execution, Specificity, Restraint, and Variety. Anything below 3, revise. Reference `tokens.css` for every value via `var(--...)`; never improvise a color, font, or space inline.

## 7. Anti-slop tells to avoid
Indigo or purple gradients; pure black; oversaturated accents; reflexive Inter or serif defaults; three-equal-cards feature rows; eyebrows above every section; section-number labels; middle-dot separators; version stamps; fake product UI, metrics, logos, or testimonials; identical repeated zigzag sections. The linter and `picasso:review` catch many of these; treat a flag as a prompt to reconsider, not to silence.

## 8. Details that signal quality
Clicking a label focuses its input. Tactile `:active`. Skeletons that match the real layout. Composed empty states. Inline, contextual errors. Every interactive component ships eight states: default, hover, focus-visible, active, disabled, loading, error, success.
