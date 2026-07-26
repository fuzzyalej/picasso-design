# picasso

A Claude Code plugin that installs a **design framework** into any project, so Claude builds interfaces with taste (minimalist, deliberate, accessible) instead of generic AI slop.

Most AI-built UIs converge on the same look: an indigo-to-purple gradient hero, three equal rounded cards, an eyebrow label above every section, a fake dashboard screenshot, and copy full of "seamlessly elevate your workflow." picasso pushes the other way. It helps you commit to one deliberate design system, writes it down as durable artifacts your project can reference, and then keeps the work honest with a linter that flags the usual tells.

## Install

picasso is distributed through the [diagon-alley](https://github.com/fuzzyalej/diagon-alley) marketplace.

```
/plugin marketplace add fuzzyalej/diagon-alley
/plugin install picasso@diagon-alley
```

Requires `python3` (standard library only, no third-party packages).

## Quick start

In any project, run the guided wizard:

```
/picasso:init
```

It runs as a coordinated, phase-gated wizard: it asks a few focused questions, scaffolds a `design-system/` folder, then works through brand, tokens, components, and demos in gated phases, showing visual option-pickers along the way. When it finishes, open `design-system/design_system.html` and `design-system/brandbook.html` in a browser to review the system visually.

## Commands

| Command | What it does |
| --- | --- |
| `/picasso:init` | Coordinated, phase-gated wizard with visual option-pickers: interview, scaffold, then populate the whole design system and review it. |
| `/picasso:brandbook` | Generate or refresh the brandbook (foundation, voice and tone, values, visual identity). |
| `/picasso:system` | Generate or refresh `design.md` (theme, color roles, type, components, layout, motion, banned anti-patterns). |
| `/picasso:tokens` | Generate or refresh `tokens.css`, the source of truth. |
| `/picasso:components` | Generate or refresh `components.css`, the reusable component layer built from tokens. |
| `/picasso:demo` | Generate demo screens that compose the components, including loading, empty, and error states. |
| `/picasso:showcase` | Assemble or refresh `design_system.html`, the unified page showing brand, palette, type, components, and the contrast matrix. |
| `/picasso:review` | Audit the design artifacts and copy against the tokens and brandbook, and report slop tells. No auto-fix. |

## What it creates

Everything lives in one folder (default `design-system/`, you choose the name at init):

```
design-system/
  brandbook.md          Foundation, voice and tone, values, visual identity
  brandbook.html        A shareable, rendered brand board
  design.md             The design system in a 9-section format, with tunable dials
  tokens.css            The source of truth: every color, type, space, radius, shadow, motion value
  components.css        The reusable component layer, built from tokens.css
  design_system.html    A unified render: brand, palette, type, values, every component, and a contrast matrix
  demo/                 Standalone demo screens (composition for feedback, not a feature mirror)
  design-instructions.md  How Claude works with these files, referenced from CLAUDE.md
```

`tokens.css` is the single source of truth. Everything else references it through `var(--...)`, and the plugin's linter treats an improvised inline value as a defect.

## How it fights slop

- **Baked into generation.** Seven skills (`taste`, `brand`, `tokens-and-system`, `motion`, `unslop-copy`, `accessibility`, `components`) carry the know-how, so output starts good rather than being cleaned up after.
- **A warn-only lint hook.** As you edit HTML, CSS, and copy, a background hook flags known tells (indigo/purple gradients, pure black, inline hex, fabricated metrics, eyebrow overuse, missing image alt text, removed focus outlines, unlabeled clickable divs, and more). It informs, it never blocks.
- **An explicit audit.** `/picasso:review` walks the design system and reports drift against the tokens and brandbook, including a WCAG AA contrast check on the conventional token pairs, so you can catch it deliberately.

## Tuning the rules

Every check the linter and reviewer run is a criterion in `rules/core.json`, not
hardcoded. A project can override or extend the shipped set by editing its own
`design-system/rules.json` (the scaffold creates it empty). Add a new
identifier to introduce a rule, or reuse an existing one to override it:

```json
{
  "picassoRulesVersion": "1",
  "rules": [
    {
      "identifier": "no-serif-headings",
      "title": "Headings stay sans-serif",
      "statement": "Heading elements must not use a serif font.",
      "level": "must-not",
      "category": "visual-design",
      "verification": "automated",
      "message": "Heading uses a serif font; use --font-sans.",
      "check": {"scheme": "regex", "kinds": ["css"], "pattern": "h[1-6]\\s*\\{[^}]*serif"},
      "examples": [
        {"outcome": "fail", "kind": "css", "content": "h1{font-family:serif;}"},
        {"outcome": "pass", "kind": "css", "content": "h1{font-family:var(--font-sans);}"}
      ]
    },
    {"identifier": "grid-1fr", "disabled": true}
  ]
}
```

The first entry adds a project-specific rule; the second turns off a shipped
one by identifier. See `docs/reference.md` for the full field reference,
schemes, and merge semantics.

## Documentation

- [Architecture](docs/architecture.md): how the engine, scripts, hook, commands, skills, and templates fit together.
- [The anti-slop approach](docs/anti-slop.md): the philosophy, the specific tells it targets, and why structure (not vocabulary) is the deepest one.
- [Technical reference](docs/reference.md): the lint rules, token taxonomy, the review and scaffold CLIs, and the `design.md` format.

## License

MIT. See [LICENSE](LICENSE).
