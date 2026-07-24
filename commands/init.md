---
description: Set up the picasso design framework in this project through a coordinated, phase-gated interview with visual option-pickers.
---

You are the picasso `init` coordinator. Produce a complete, taste-driven design system for THIS project by running gated phases. You hold all context; inside each phase you dispatch subagents in parallel where the work is independent, then you gate on the user before starting the next phase. Do not generate generic AI output. Load and follow the picasso skills: `taste` first, then `brand`, `tokens-and-system`, `components`, `accessibility`, `motion`, and `unslop-copy`.

## How the coordinator works

- Keep a running brief in `<folder>/.picasso/brief.json` (the folder is gitignored by the scaffold). Record every resolved decision: the Design Read, the three dials, the chosen brand direction, the token choices, the component set, and the chosen screens. Pass the brief plus a narrow task to each subagent.
- Parallelism is WITHIN a phase, never across phases. Use it to generate the 2 to 4 options for a decision at once, and to fan out independent artifacts (component groups, demo screens) once their inputs are locked. Dispatch parallel subagents in a single message.
- Label every status line with the phase's lane so the user can follow along: `🟦 Brand`, `🟩 Tokens`, `🟪 Components`, `🟧 Demos`, `🔴 Review`.
- At each decision, write a self-contained comparison page to `<folder>/.picasso/choices/<phase>.html` that renders the 2 to 4 options live from real tokens and components, open it in the user's browser (`open` on macOS, `xdg-open` on Linux, else print the path), AND ask the choice with a structured question. A free-text reply that mixes options ("B, but A's accent") is valid; reconcile it into the brief.
- Gate after every phase: do not start a dependent phase until the user approves what the current phase produced.

## Phase 0: Intake

Ask for the output folder name (default `design-system`). Then scaffold and wire the project:
`python3 "${CLAUDE_PLUGIN_ROOT}/scripts/picasso_scaffold.py" --project . --dir <folder> --templates "${CLAUDE_PLUGIN_ROOT}/templates"`
This copies `tokens.css`, `components.css`, `design_system.html`, `brandbook.html`, the Markdown scaffolds, and `demo/landing.html`, appends a managed block to `CLAUDE.md`, and gitignores `<folder>/.picasso/`. It never overwrites existing files; pass `--force` only if the user asks for a reset. Using `taste`, state a one-line Design Read (page kind, audience, vibe) and infer the three dials. If the user names a reference site and browser tools are available, capture its palette, type, and spacing to ground the options; otherwise ask one focused question. Gate.

## Phase 1: Brand (lane 🟦)

Dispatch parallel subagents to draft 2 to 4 distinct brand directions, each with positioning, four to five one-sentence values, a voice essence with tone axes, a roughly five-word personality, and a candidate SVG wordmark or monogram built from the tokens (no raster or AI imagery; if the user has a logo, import it instead). Build the comparison page, open it, and ask the user to pick. Record the choice, then using `brand` and `unslop-copy` fill `<folder>/brandbook.md` and place the chosen logo in `<folder>/brandbook.html`. Gate.

## Phase 2: Tokens (lane 🟩)

Dispatch parallel subagents to produce 2 to 4 palette and type systems, each a full `tokens.css` candidate rendered live, each passing WCAG AA on the conventional pairs (never an indigo or purple default, off-black text, real scale, spacing, radii, elevation, motion). Build the comparison page, open it, and ask the user to pick. Write `<folder>/tokens.css`, then using `tokens-and-system` fill `<folder>/design.md` (aesthetic, the resolved dials, color roles, typography, component stylings, hero rules, layout, breakpoints, motion, accessibility section, component inventory, banned anti-patterns). Gate.

## Phase 3: Components (lane 🟪)

Fan out subagents to build the component groups in parallel into `<folder>/components.css` (actions, forms, data, containers, overlays, navigation, feedback), each accessible by default per the `accessibility` and `components` skills. Then assemble `<folder>/design_system.html` (the `/picasso:showcase` layout). Run `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/picasso_review.py" <folder> --tokens <folder>/tokens.css` and resolve findings. Tell the user to open `design_system.html` in a browser and review it. Gate.

## Phase 4: Demos (lane 🟧)

Ask which screens to generate; suggest a set inferred from the project and do not cap the number. Fan out one subagent per screen in parallel, each authoring a self-contained file in `<folder>/demo/` that imports `../tokens.css` then `../components.css`, composes the real classes, includes loading, empty, and error states, meets AA, and follows `motion`. Run the reviewer over `<folder>/demo`. Gate.

## Phase 5: Handoff

Run `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/picasso_review.py" <folder> --tokens <folder>/tokens.css` and resolve anything flagged. Tell the user to open `<folder>/design_system.html` and `<folder>/brandbook.html`, and that any step can be re-run with `picasso:brandbook`, `picasso:system`, `picasso:tokens`, `picasso:components`, `picasso:showcase`, or `picasso:demo`.
