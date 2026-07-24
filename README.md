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

It asks a few focused questions, scaffolds a `design-system/` folder, and populates it with a brandbook, a design system, design tokens, and demo screens tuned to your project. When it finishes, open `design-system/styleguide.html` and `design-system/brandbook.html` in a browser to review the system visually.

## Commands

| Command | What it does |
| --- | --- |
| `/picasso:init` | Guided wizard: interview, scaffold, then populate the whole design system and review it. |
| `/picasso:brandbook` | Generate or refresh the brandbook (foundation, voice and tone, values, visual identity). |
| `/picasso:system` | Generate or refresh `design.md` (theme, color roles, type, components, layout, motion, banned anti-patterns). |
| `/picasso:tokens` | Generate or refresh `tokens.css`, the source of truth, plus its styleguide. |
| `/picasso:demo` | Generate demo screens that compose the components, including loading, empty, and error states. |
| `/picasso:review` | Audit the design artifacts and copy against the tokens and brandbook, and report slop tells. No auto-fix. |

## What it creates

Everything lives in one folder (default `design-system/`, you choose the name at init):

```
design-system/
  brandbook.md          Foundation, voice and tone, values, visual identity
  brandbook.html        A shareable, rendered brand board
  design.md             The design system in a 9-section format, with tunable dials
  tokens.css            The source of truth: every color, type, space, radius, shadow, motion value
  styleguide.html       A live render of tokens.css (swatches, type scale, components in 8 states)
  demo/                 Standalone demo screens (composition for feedback, not a feature mirror)
  design-instructions.md  How Claude works with these files, referenced from CLAUDE.md
```

`tokens.css` is the single source of truth. Everything else references it through `var(--...)`, and the plugin's linter treats an improvised inline value as a defect.

## How it fights slop

- **Baked into generation.** Five skills (`taste`, `brand`, `tokens-and-system`, `motion`, `unslop-copy`) carry the know-how, so output starts good rather than being cleaned up after.
- **A warn-only lint hook.** As you edit HTML, CSS, and copy, a background hook flags known tells (indigo/purple gradients, pure black, inline hex, fabricated metrics, eyebrow overuse, and more). It informs, it never blocks.
- **An explicit audit.** `/picasso:review` walks the design system and reports drift against the tokens and brandbook, so you can catch it deliberately.

## Documentation

- [Architecture](docs/architecture.md): how the engine, scripts, hook, commands, skills, and templates fit together.
- [The anti-slop approach](docs/anti-slop.md): the philosophy, the specific tells it targets, and why structure (not vocabulary) is the deepest one.
- [Technical reference](docs/reference.md): the lint rules, token taxonomy, the review and scaffold CLIs, and the `design.md` format.

## License

MIT. See [LICENSE](LICENSE).
