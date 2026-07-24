---
description: Set up the picasso design framework in this project (brandbook, design system, tokens, demo screens) through a guided interview.
---

You are running the picasso `init` wizard. Produce a complete, taste-driven design system for THIS project. Do not generate generic AI output. Load and follow the picasso skills, `taste` first, then `brand`, `tokens-and-system`, `motion`, and `unslop-copy`.

Work through these steps, pausing for the user where noted.

1. Folder. Ask the user for the output folder name (default `design-system`).

2. Scaffold. Lay down the starting templates and wire CLAUDE.md:
   `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/picasso_scaffold.py" --project . --dir <folder> --templates "${CLAUDE_PLUGIN_ROOT}/templates"`
   This copies `tokens.css`, `styleguide.html`, `brandbook.html`, the Markdown scaffolds, and `demo/landing.html`, and appends a managed block to `CLAUDE.md`. It never overwrites existing files; pass `--force` only if the user asks for a reset.

3. Design Read. Using `taste`, state a one-line Design Read (page kind, audience, vibe) and infer the three dials. If the user names a reference site and browser tools are available, capture its palette, type, and spacing to ground the tokens; otherwise ask one focused question. Extract principles, never clone.

4. Brandbook. Using `brand` and `unslop-copy`, fill `<folder>/brandbook.md` with real, project-specific content: foundation (mission, vision, 4 to 5 one-sentence values, roughly five-word personality, positioning), verbal identity (voice essence, tone axes, voice do and don't, things we never say), visual identity, and a consolidated Brand Don'ts list. Leave `<folder>/brandbook.html` as-is; it renders from the tokens.

5. Tokens and system. Using `tokens-and-system`, edit `<folder>/tokens.css` so the values reflect this project: one deliberate accent (never an indigo or purple default), off-black text, a real type scale, spacing, radii, elevation, and motion. Then fill `<folder>/design.md`: aesthetic in one line, the resolved dials, color roles, typography, component stylings, hero rules, layout, responsive breakpoints, motion, and the banned anti-patterns. Everything downstream references `var(--...)`.

6. Demo screens. Ask the user which screens to generate. Suggest a set inferred from the project and do not cap the number. For each, author a self-contained HTML file in `<folder>/demo/` that imports `../tokens.css`, composes real components, and includes loading (skeleton matching layout), empty, and error states. These are compositions for feedback, not a mirror of real features. Follow `motion` for any animation.

7. Review. Run `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/picasso_review.py" <folder>` and resolve anything it flags.

8. Hand off. Tell the user to open `<folder>/styleguide.html` and `<folder>/brandbook.html` in a browser to review the system, and that any step can be re-run with `picasso:brandbook`, `picasso:system`, `picasso:tokens`, or `picasso:demo`.
