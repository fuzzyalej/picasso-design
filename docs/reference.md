# Technical reference

## The rule layer (`picasso_engine.rules`, `rules.py`, `rules_render.py`)

The eleven original lint rules plus the four structural checks below are no
longer hardcoded — they are data. The shipped set lives in `rules/core.json`
(18 criteria as of this writing: 15 automated — `em-dash`, `pure-black`,
`fake-metric`, `inline-hex`, `img-alt`, `focus-removed`,
`clickable-nonsemantic`, `purple-gradient`, `eyebrow-overuse`, `grid-1fr`,
`duplicate-cta`, `contrast`, `external-dep`, `undefined-token`,
`component-use-cases` — plus 3 manual hero criteria (`hero-fits-viewport`,
`hero-headline-lines`, `hero-subtext-length`) that carry no `check` and
route into `design.md`'s "Review by hand" section), stamped with a
`picassoRulesVersion`. A project can add its own `design-system/rules.json`,
which the loader merges over core.

### Criterion fields

Each entry in a rules file's `rules` array is a criterion:

| Field | Required | Notes |
| --- | --- | --- |
| `identifier` | yes | Kebab-case, unique within the merged set. |
| `title` | yes | Short human-readable name. |
| `statement` | yes | The rule itself, as prose. |
| `level` | yes | One of `must`, `must-not`, `should`, `should-not` (RFC 2119). `must`/`must-not` report as `warn`; `should`/`should-not` report as `info`. |
| `category` | yes | One of `visual-design`, `interaction`, `accessibility`, `content`, `motion`, `development`. |
| `verification` | yes | `automated` (has a `check`, is linted), `assisted`, or `manual` (neither is linted; both are prose-only). |
| `message` | for automated rules | The finding text shown to the user. |
| `check` | for automated rules | One check object, or a list of them. A list is a union, not a conjunction: each check is evaluated independently and any check that matches produces its own finding, so a criterion whose checks both match the same input reports twice — hits are not deduplicated across checks within a criterion (see schemes below). |
| `examples` | for automated rules | At least one entry with `"outcome": "pass"` and one with `"outcome": "fail"`, each `{"outcome", "kind", "content"}`. Used by the conformance tests, not at runtime. |
| `rationale` | no | Why the rule exists. Must not just restate `statement`. |
| `evidence` | no | Free-text backing for the rationale. |
| `references` | no | A list of citations or links. |
| `target` | no | Routes the rule into a `design.md` managed block: `color`, `typography`, `hero`, `global`, or (implicitly) `manual` for anything not `automated`. |
| `disabled` | project files only | `true` removes a core rule by identifier. Rejected in `rules/core.json` itself. |

`validate_rules(raw, allow_disabled=False)` returns a list of human-readable
errors (empty means valid); it never raises. `load_rules(project_path=None)`
returns `(criteria, errors)` and always degrades to the shipped rules on a
broken or absent project file.

### Schemes

A `check` names a `scheme` and that scheme's own keys:

- **`regex`** — `kinds` (required list drawn from `html`, `css`, `copy`),
  `pattern` (required), `flags` (a string of `i`/`s`/`m`), and four modifiers:
  `strip`, `within`, `absent`, `skipIfFileMatches`. Applied in this fixed
  order:
  1. `skipIfFileMatches` — evaluated once against the whole file; if it
     matches, the check is skipped entirely.
  2. `strip` — a list of patterns removed from each line before matching.
  3. `within` — narrows the haystack to the capture group (`group`, default
     `1`) of a containing pattern, so the rule matches inside e.g. a `style=`
     attribute rather than the whole line.
  4. `pattern` — the match itself, run against what `strip`/`within` left.
  5. `absent` — if it matches inside the same hit, the hit is discarded (an
     exception carved out of an otherwise-matching line).
- **`token-pair`** — `pairs` (a list of `[foreground, background]` token name
  pairs) and `minRatio` (default `4.5`). Evaluated against the token map from
  `tokens.css`, not file content; a rule mixing `token-pair` with any other
  scheme in the same `check` list is rejected by `validate_rules` — the two
  are incoherent together (one reads tokens, the other reads content).
- **`builtin`** — `kinds` plus `name`, for the checks that compute rather than
  match. `name` is one of the seven registered functions in
  `picasso_engine.schemes.BUILTINS`: `purple_gradient`, `eyebrow_overuse`,
  `grid_1fr`, `duplicate_cta`, `external_deps_check`, `undefined_token_refs`,
  `component_use_cases`. `validate_rules` rejects an unrecognized name, and
  rejects a builtin check that omits `kinds`.

  `kinds` means the same thing here as for `regex` and is enforced in the same
  place — `run_check` gates on it before dispatching, so a builtin never sees a
  kind its rule did not declare. This is why the JSON alone tells you when a
  rule runs: `{"scheme": "builtin", "name": "purple_gradient", "kinds": ["html", "css"]}`
  says plainly that the rule skips prose, without reading any Python.

  Writing a new builtin: the registry maps a name to
  `callable(content, kind, tokens) -> iterable of (line_number, snippet)`.
  Yield tuples, not `Finding` objects — `findings_for` attaches the identifier,
  the derived severity, and the message. Do not gate on `kind` inside the
  function; declare `kinds` in the JSON instead. Do gate on `tokens`, which is
  `None` on the hook path (see "Tokens and the hook" below).

### Tokens and the hook

`tokens` is `None` on the hook path and a dict on the review path, and the
difference is deliberate:

- **`None`** — the write hook lints one file on save and has no token map, so it
  passes `None`. The `token-pair` scheme and `undefined_token_refs` yield nothing
  rather than guessing. Without this, every `var()` reference in every edited
  file would be reported as an undefined token.
- **`{}`** — an empty map means `tokens.css` was looked for and its properties
  are genuinely absent, so every `var()` reference *is* undefined and is
  reported. This preserves the reviewer's pre-existing behaviour.

The consequence worth knowing: `contrast`, `undefined-token`, and
`component-use-cases` never fire on the hook path. Editing `design.md` will not
warn you about an undocumented component — that surfaces when you run
`/picasso:review`. `contrast` is also skipped entirely when no `tokens.css` is
found, since there are no pairs to compare.

### Merge semantics

`merge(core, project)` layers a project's criteria over the shipped set by
identifier:

- A new identifier is **appended**.
- An existing identifier is **replaced** in place (position preserved).
- `{"identifier": "<id>", "disabled": true}` **removes** that core rule from
  the merged set. `disabled` is only valid in a project rules file —
  `rules/core.json` rejects it.

### Rendering and finding kinds

`rules_render.render_all(existing_markdown, criteria)` fills `design.md`'s
five managed blocks (routed by `target`, with non-automated rules landing in
the manual block) from the current rule set. `rules_render.stale_blocks`
reports which blocks no longer match a fresh render.

`picasso_review.py` adds two finding kinds on top of the per-file lint
results:

- **`rules-invalid`** (`warn`) — the merged rule set failed validation (an
  invalid core or project file); the review falls back to the shipped rules
  and reports why.
- **`rules-stale`** (`info`) — one of `design.md`'s managed blocks no longer
  matches what the current rules would render; re-render it or move the edit
  into `rules.json`.

### A note on trust

Patterns in `design-system/rules.json` are compiled and executed by the lint hook
on every write. A pathological pattern can therefore hang the hook.

picasso does not sandbox these patterns and does not screen them. `rules.json` is
a file in your own repository, trusted at the same level as `CLAUDE.md`. This is
a documented limit, not a security boundary — do not paste a rules file from a
source you would not paste a shell script from.

## Lint rules

`picasso_engine.slop_lint.lint(content, kind, tokens=None, rules=None)` returns a list of `Finding(rule, severity, message, line, snippet)`. `kind` is `"html"`, `"css"`, or `"copy"` (Markdown). Rules apply per kind. The table below documents the eleven original rules; they are now criteria in `rules/core.json` rather than hardcoded, but behave identically.

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
python3 scripts/picasso_review.py [path ...] [--tokens PATH] [--rules PATH]
```

- `path` defaults to `design-system`. Directories are walked for `.html`, `.htm`, `.css`, `.md` files.
- `--tokens` points at the `tokens.css` used for `undefined-token` and `contrast` checks. If omitted, it auto-detects `tokens.css` under the first path, then `design-system/tokens.css`.
- `--rules` points at a project `rules.json` to merge over the shipped set. If omitted, it walks up from the tokens path (or the first path given) looking for a sibling `rules.json`.
- Always exits 0. Prints a report grouped by file, or a clean message. A broken or invalid rules file reports a `rules-invalid` finding and falls back to the shipped rules rather than failing the run.

### `picasso_scaffold.py`

```
python3 scripts/picasso_scaffold.py --project . --dir design-system --templates <templates-dir> [--force]
python3 scripts/picasso_scaffold.py --project . --dir design-system --render
```

- Copies the template files (`tokens.css`, `components.css`, `design_system.html`, `brandbook.html`, `design.md`, `brandbook.md`, `design-instructions.md`, `demo/landing.html`) into `<project>/<dir>/`, creating directories.
- Writes an empty `<project>/<dir>/rules.json` (`{"picassoRulesVersion": "1", "rules": []}`) for the project to tune later, and renders `design.md`'s managed rule blocks from the current rule set so a fresh scaffold starts in sync.
- Skips files that already exist unless `--force`.
- Wires a managed `<!-- picasso:start -->` block into `<project>/CLAUDE.md` pointing at `<dir>/design-instructions.md`. Idempotent, and preserves any existing CLAUDE.md content.
- Adds `<dir>/.picasso/` to `<project>/.gitignore` (creating the file if needed), so the coordinator's working state (the running brief and option-picker pages) never gets committed.
- `--render` re-renders an existing `<dir>/design.md`'s managed rule blocks in place from the merged (core + project) rule set, then exits — no template copying, no `CLAUDE.md` wiring, no `rules.json` write, and `--templates` is not required. This is the fix for a `rules-stale` finding: it closes the drift loop without `--force`'s destructive full-file overwrite.

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
