# Architecture

picasso is a Claude Code plugin. It ships no runtime dependency into your project: it produces artifacts (Markdown, CSS, HTML) and audits them. The moving parts split into six layers.

```
commands/            user-facing prompts  (/picasso:init, :brandbook, :system, :tokens, :components, :demo, :showcase, :review)
skills/              the know-how they load (taste, brand, tokens-and-system, motion, unslop-copy, accessibility, components)
rules/core.json      the shipped rule set, as data
scripts/             mechanical work       (picasso_scaffold.py, picasso_review.py)
  picasso_engine/    the reusable core     (rules, schemes, slop_lint, rules_render, tokens, artifact_check, claude_md, kinds, frontmatter, contrast)
hooks/               the warn-only lint hook wiring
templates/           the design-system artifacts that get copied into a project
```

## The engine (`scripts/picasso_engine/`)

Pure Python, standard library only, fully unit-tested. This is the reusable core that both the hook and the scripts build on.

- **`rules.py`** holds the criterion model and the rule set's plumbing:
  `validate_rules`, `load_rules(project_path)`, and `find_project_rules(path)`.
  Loading never raises — it returns `(criteria, errors)` so every caller can
  degrade to the shipped rules.
- **`schemes.py`** executes checks. Three schemes: `regex` (a pattern plus the
  `strip`, `within`, `absent`, and `skipIfFileMatches` modifiers), `token-pair`
  (contrast between two token names), and `builtin` (a named Python function, for
  the seven checks that compute rather than match).
- **`slop_lint.py`** exposes `lint(content, kind, tokens=None, rules=None) -> list[Finding]`.
  It is a dispatcher: it loads the merged rule set, runs each automated
  criterion, and sorts the findings. `Finding.rule` carries the criterion
  identifier; severity derives from the RFC 2119 level, with `must`/`must-not`
  reporting as `warn` and `should`/`should-not` as `info`.
- **`rules_render.py`** renders criteria into `design.md`'s managed blocks,
  routed by each rule's `target`, and reports which blocks have drifted.
- **`tokens.py`** exposes `parse_tokens(css) -> dict`, mapping each CSS custom property (without the leading `--`) to its declared value. This is how the linter and validator know which tokens exist.
- **`artifact_check.py`** exposes `external_deps(content)` (any `http(s)://`, protocol-relative, `@import`, or `srcset` reference to an external host) and `undefined_var_refs(content, tokens)` (any `var(--x)` not defined in the tokens). Together they prove an artifact is self-contained and token-consistent.
- **`contrast.py`** exposes `parse_color(value)` (hex or `rgb()`/`rgba()` to an `(r, g, b)` tuple), `relative_luminance(rgb)`, `contrast_ratio(fg, bg)` (the WCAG ratio between two colors), and `passes_aa(fg, bg, large=False)` (whether the pair clears 4.5:1, or 3.0:1 for large or UI text). This is how the review checks token pairs for accessible contrast.
- **`claude_md.py`** exposes `upsert_managed_block(existing, body)`, an idempotent writer that inserts or replaces a delimited block in `CLAUDE.md` without disturbing surrounding content.
- **`kinds.py`** centralizes the file-extension to lint-kind mapping (`kind_for`).
- **`frontmatter.py`** parses the simple `---` frontmatter fences used by commands and skills.

## The scripts (`scripts/`)

Thin CLIs over the engine. Each inserts its own directory on `sys.path` so it resolves the engine when run standalone as `${CLAUDE_PLUGIN_ROOT}/scripts/<name>.py`.

- **`picasso_scaffold.py`** copies the template files (`tokens.css`, `components.css`, `design_system.html`, `brandbook.html`, `design.md`, `brandbook.md`, `design-instructions.md`, `demo/landing.html`) into the chosen folder, appending a one-line `stamp_for(kind)` provenance comment to each as it is written; writes an empty `rules.json` (`{"picassoRulesVersion": "1", "rules": []}`) for the project to tune later; re-renders `design.md`'s managed rule blocks from the current rule set so a fresh scaffold starts in sync; wires a managed block into `CLAUDE.md` via `upsert_managed_block`; and adds `<folder>/.picasso/` to the project's `.gitignore` (the coordinator's working state, such as the running brief and option-picker pages, lives there). It skips files that already exist unless `--force`, so re-running never clobbers your customizations.
- **`picasso_review.py`** walks a path (file or directory), runs `lint` plus the structural checks per file, checks the conventional token pairs for WCAG AA contrast via `contrast.py`, and prints a report grouped by file. It is advisory: it always exits 0 and never edits anything.

## The hook (`hooks/`)

A `PostToolUse` hook matches `Write|Edit|MultiEdit` and runs `slop_lint_hook.py`. The hook reads the tool payload, lints the written file by extension, prints any tells to stderr, and always exits 0. It is warn-only by design: a design linter that blocks edits fights the author, so this one only informs. It also degrades safely, swallowing any internal error rather than interrupting your session.

## Commands and skills

Commands are Markdown prompts. They orchestrate the interactive and creative work (interviewing, generating the brandbook, tuning tokens, composing demo screens) and shell out to the scripts for the mechanical steps. They load skills for the judgment.

Skills are the durable know-how, kept separate from any one command so every command draws on the same standards:

- **`taste`** is loaded first for any UI work. It sets the Design Read, the three dials, the consistency locks, and the anti-slop tells.
- **`brand`** structures the brandbook into concrete, reference-backed content.
- **`tokens-and-system`** defines the token taxonomy, the source-of-truth discipline, and the `design.md` format.
- **`components`** defines the reusable component layer (`components.css`): its class conventions, variant and state naming, and how demos and `design_system.html` consume it.
- **`accessibility`** encodes the WCAG AA bar picasso enforces: contrast, focus, keyboard, semantics and ARIA, motion, and hit targets, and how each maps to a lint rule or the review's contrast check.
- **`motion`** keeps animation motivated, cheap to render, and reduced-motion aware.
- **`unslop-copy`** removes AI-slop tells from prose in three passes.

## Data flow: what `/picasso:init` does

`/picasso:init` is a coordinator, not a linear script. It holds the running context itself, keeps a brief in `<folder>/.picasso/brief.json`, and works through gated phases. Inside a phase it dispatches subagents in parallel wherever the work is independent (generating option sets, or fanning out once inputs are locked); it never parallelizes across phases, and it gates on user approval before starting the next one. Each phase is labeled with a lane so progress is visible:

```
Phase 0: Intake            ->  ask the folder name, scaffold + wire CLAUDE.md and .gitignore,
                                a one-line Design Read + the three dials.               Gate.
Phase 1: Brand      (🟦)   ->  parallel brand direction options (positioning, values,
                                voice, a candidate logo); user picks; fills brandbook.md
                                and brandbook.html.                                      Gate.
Phase 2: Tokens     (🟩)   ->  parallel palette/type candidates, each checked against AA;
                                user picks; writes tokens.css, then design.md.           Gate.
Phase 3: Components (🟪)   ->  parallel component groups fill components.css; assembles
                                design_system.html; picasso_review.py audits it.         Gate.
Phase 4: Demos      (🟧)   ->  parallel per-screen subagents compose demo/ from tokens.css
                                and components.css; picasso_review.py audits them.       Gate.
Phase 5: Handoff    (🔴)   ->  final picasso_review.py pass; open design_system.html and
                                brandbook.html to review.
```

Each option-driven decision renders a self-contained comparison page under `<folder>/.picasso/choices/` from real tokens and components, which the coordinator opens in the user's browser alongside a structured question; free-text answers that mix options are reconciled into the brief.

The source of truth stays `tokens.css`; `components.css` builds the reusable layer on top of it, and `design_system.html` and the demo screens render from both, so reviewing the tokens and components reviews the whole system.

## Testing

Every engine function, script, and template ships with tests (`tests/`). The templates are guarded by tests proving they are self-contained, reference only defined tokens, and are free of the tells the plugin exists to remove. One end-to-end test scaffolds a fresh project and runs the reviewer against it, asserting zero findings, which proves the shipped defaults pass their own audit.
