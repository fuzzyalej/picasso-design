---
name: motion
description: Use when adding animation or transitions in a picasso project. Motion must be motivated, cheap to render, and respect reduced-motion.
---

# Motion

Motion communicates hierarchy, feedback, or state change. If you cannot state the reason in one sentence, drop it. "It looked cool" is not a reason.

## Rules
- Animate only `transform` and `opacity`; never layout properties (top, left, width, height).
- Use the named easing tokens (`--ease-out`, `--ease-in`, `--ease-in-out`); no browser-default `ease`, no bounce or overshoot unless the aesthetic explicitly calls for it.
- Take duration from tokens (`--duration-fast`, `--duration-base`, `--duration-slow`).
- Motion claimed is motion shown: if MOTION_INTENSITY is above 4, the page actually moves (entrance, scroll-reveal, hover feedback). If you cannot ship working motion, drop the dial to 3 and ship clean static. Never half-built.
- Ration it: at most one perpetual or marquee element per page; not every card loops. Stagger list reveals with an index-based delay.

## Reduced motion
Under `prefers-reduced-motion: reduce`, spatial motion collapses to a crossfade of at most 150ms opacity. Focus rings appear instantly and are never animated.
