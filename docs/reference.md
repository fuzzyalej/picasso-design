# Technical reference

## Lint rules

`picasso_engine.slop_lint.lint(content, kind, tokens=None)` returns a list of `Finding(rule, severity, message, line, snippet)`. `kind` is `"html"`, `"css"`, or `"copy"` (Markdown). Rules apply per kind.

| Rule | Severity | Kinds | Flags |
| --- | --- | --- | --- |
| `em-dash` | warn | html, copy | Em or en dashes in copy. |
| `pure-black` | warn | html, css | `#000`, `#000000`, and opaque alpha forms. Use an off-black token. |
| `inline-hex` | warn | html, css | Raw hex outside a token declaration (inline styles, ad-hoc CSS). |
| `purple-gradient` | warn | html, css | Gradients containing indigo/purple/violet keywords or common purple hexes. |
| `eyebrow-overuse` | info | html | More all-caps kicker labels than one per three `<section>`s. |
| `fake-metric` | warn | html, copy | Marketing metrics like "+47% conversion", "trusted by 50,000", "99.9%". |
| `grid-1fr` | info | html, css | `grid-template-columns` using `1fr` instead of `minmax(0, 1fr)`. |
| `duplicate-cta` | info | html | The same button or link label repeated across CTA-classed elements. |
| `img-alt` | warn | html | An `<img>` with no `alt` attribute. Add alt text, or `alt=""` if decorative. |
| `focus-removed` | warn | html, css | A bare `outline: none`/`outline: 0` with no `:focus-visible` replacement anywhere in the file. |
| `clickable-nonsemantic` | info | html | A `div`/`span` carrying a click handler with no `role` attribute; use a real button or link, or add a role plus keyboard support. |

The `picasso_review.py` reviewer adds structural checks on top of the lint rules:

| Rule | Severity | Flags |
| --- | --- | --- |
| `external-dep` | warn | Any external reference (`http(s)://`, protocol-relative `//`, `@import`, or `srcset`) to a non-local host. |
| `undefined-token` | warn | A `var(--x)` reference not defined in the project's `tokens.css`. |
| `missing-path` | warn | A path passed to the reviewer that does not exist (guards against a typo reporting "clean"). |
| `contrast` | warn | A conventional token pair (`--color-text`/`--color-bg`, `--color-text`/`--color-surface`, `--color-text-muted`/`--color-bg`, `--color-accent-contrast`/`--color-accent`) that fails WCAG AA (below 4.5:1). |

## Contrast (`picasso_engine/contrast.py`)

Pure Python WCAG contrast math, no third-party dependency.

- `parse_color(value) -> (r, g, b) | None` parses a hex color (`#rgb`, `#rgba`, `#rrggbb`, `#rrggbbaa`) or an `rgb()`/`rgba()` string into an 0 to 255 RGB tuple. Returns `None` if the value does not parse.
- `relative_luminance(rgb) -> float` computes the WCAG relative luminance of an RGB tuple.
- `contrast_ratio(fg, bg) -> float | None` computes the WCAG contrast ratio between two color strings, or `None` if either fails to parse.
- `passes_aa(fg, bg, large=False) -> bool | None` returns whether the pair clears WCAG AA: 4.5:1 for normal text, 3.0:1 when `large=True` (large text or UI components), or `None` if unparsable.

`picasso_review.py` uses these to audit a fixed list of conventional token pairs (see the `contrast` rule above) every time it runs against a directory or file with a `--tokens` reference; a failing pair reports its actual ratio.

## Token taxonomy

`tokens.css` is the single source of truth. Tokens are `:root` custom properties, referenced everywhere via `var(--...)`. The default set covers:

- **Color:** roles, not raw names (`--color-bg`, `--color-text`, `--color-accent`, `--color-success`, `--color-danger`, and neutrals). One deliberate accent. Off-black text, never pure black. Light and dark via `prefers-color-scheme`.
- **Typography:** `--font-sans`, `--font-mono`, a size scale, line heights, tracking.
- **Spacing:** a 4px-based ramp.
- **Size:** container widths and a `--size-tap` of at least 44px.
- **Shape:** the radius scale.
- **Elevation:** shadows.
- **Motion:** durations and three named easings (`--ease-out`, `--ease-in`, `--ease-in-out`).

## The `design.md` format

Nine sections, each visual section carrying its own inline "Banned" subsection:

```
0. Aesthetic in one line
   Configuration (the three dials: DESIGN_VARIANCE, MOTION_INTENSITY, VISUAL_DENSITY)
1. Visual theme and atmosphere
2. Color palette and roles          (name, token, role, rationale; Banned Colors)
3. Typography rules                 (families, scale; Banned Fonts)
4. Component stylings               (buttons, cards, inputs, nav, loaders, empty, error; 8 states each)
5. Hero / signature section         (fits viewport; Banned: fake UI, invented metrics, version stamps)
6. Layout principles                (grid-first, contained max-width)
7. Responsive rules                 (named breakpoints; test 375 / 768 / 1440)
8. Motion and interaction
9. Anti-patterns (banned)
```

Every interactive component ships eight states: default, hover, focus-visible, active, disabled, loading, error, success.

## CLIs

### `picasso_review.py`

```
python3 scripts/picasso_review.py [path ...] [--tokens PATH]
```

- `path` defaults to `design-system`. Directories are walked for `.html`, `.htm`, `.css`, `.md` files.
- `--tokens` points at the `tokens.css` used for `undefined-token` and `contrast` checks. If omitted, it auto-detects `tokens.css` under the first path, then `design-system/tokens.css`.
- Always exits 0. Prints a report grouped by file, or a clean message.

### `picasso_scaffold.py`

```
python3 scripts/picasso_scaffold.py --project . --dir design-system --templates <templates-dir> [--force]
```

- Copies the template files (`tokens.css`, `components.css`, `design_system.html`, `brandbook.html`, `design.md`, `brandbook.md`, `design-instructions.md`, `demo/landing.html`) into `<project>/<dir>/`, creating directories.
- Skips files that already exist unless `--force`.
- Wires a managed `<!-- picasso:start -->` block into `<project>/CLAUDE.md` pointing at `<dir>/design-instructions.md`. Idempotent, and preserves any existing CLAUDE.md content.
- Adds `<dir>/.picasso/` to `<project>/.gitignore` (creating the file if needed), so the coordinator's working state (the running brief and option-picker pages) never gets committed.

## Commands and skills

Two commands generate the layers this plan added:

- **`/picasso:components`** generates or refreshes `components.css`, the reusable component layer built from `tokens.css` (actions, form fields, tables, badges, cards, overlays, navigation and tabs, alerts, and the loading, empty, and error states), then runs `picasso_review.py` against it.
- **`/picasso:showcase`** assembles or refreshes `design_system.html`, the single page showing brand, values, palette, type scale, the full component gallery, and a contrast section that computes each conventional token pair's ratio at runtime, then runs `picasso_review.py` against it.

Two skills back the accessibility and component work:

- **`accessibility`** is the WCAG AA bar picasso enforces: contrast ratios for the conventional token pairs, visible focus via `:focus-visible`, keyboard operability, semantic markup and ARIA only where semantics cannot reach, reduced-motion handling, and 44px hit targets. It is the skill behind the `contrast`, `img-alt`, `focus-removed`, and `clickable-nonsemantic` checks.
- **`components`** defines `components.css`'s conventions: semantic, stack-agnostic class names (`.btn`, `.field`, `.card`, `.modal`, and so on), a `--modifier` suffix for variants, attribute or `is-` classes for state, and the rule that pages and demos consume the layer rather than re-declaring component styles.

## Precedence

When `tokens.css`, `design.md`, or `brandbook.md` exist at their expected locations, they govern. Claude reads them first and does not contradict them; the skills extend an existing system rather than silently replacing it.

## Requirements

`python3` (3.9 or newer), standard library only. No third-party runtime dependencies. Tests run with `pytest`.
