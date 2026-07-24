# Architecture

picasso is a Claude Code plugin. It ships no runtime dependency into your project: it produces artifacts (Markdown, CSS, HTML) and audits them. The moving parts split into five layers.

```
commands/            user-facing prompts  (/picasso:init, :brandbook, :system, :tokens, :demo, :review)
skills/              the know-how they load (taste, brand, tokens-and-system, motion, unslop-copy)
scripts/             mechanical work       (picasso_scaffold.py, picasso_review.py)
  picasso_engine/    the reusable core     (slop_lint, tokens, artifact_check, claude_md, kinds, frontmatter)
hooks/               the warn-only lint hook wiring
templates/           the design-system artifacts that get copied into a project
```

## The engine (`scripts/picasso_engine/`)

Pure Python, standard library only, fully unit-tested. This is the reusable core that both the hook and the scripts build on.

- **`slop_lint.py`** exposes `lint(content, kind, tokens=None) -> list[Finding]`, where `kind` is `"html"`, `"css"`, or `"copy"`. It runs eight regex-based rules (see the [reference](reference.md)). Each result is a `Finding(rule, severity, message, line, snippet)` with severity `"warn"` or `"info"`. The rules are deliberately grep-shaped: cheap, explainable, and resistant to false confidence.
- **`tokens.py`** exposes `parse_tokens(css) -> dict`, mapping each CSS custom property (without the leading `--`) to its declared value. This is how the linter and validator know which tokens exist.
- **`artifact_check.py`** exposes `external_deps(content)` (any `http(s)://`, protocol-relative, `@import`, or `srcset` reference to an external host) and `undefined_var_refs(content, tokens)` (any `var(--x)` not defined in the tokens). Together they prove an artifact is self-contained and token-consistent.
- **`claude_md.py`** exposes `upsert_managed_block(existing, body)`, an idempotent writer that inserts or replaces a delimited block in `CLAUDE.md` without disturbing surrounding content.
- **`kinds.py`** centralizes the file-extension to lint-kind mapping (`kind_for`).
- **`frontmatter.py`** parses the simple `---` frontmatter fences used by commands and skills.

## The scripts (`scripts/`)

Thin CLIs over the engine. Each inserts its own directory on `sys.path` so it resolves the engine when run standalone as `${CLAUDE_PLUGIN_ROOT}/scripts/<name>.py`.

- **`picasso_scaffold.py`** copies the seven template files into the chosen folder and wires a managed block into `CLAUDE.md` via `upsert_managed_block`. It skips files that already exist unless `--force`, so re-running never clobbers your customizations.
- **`picasso_review.py`** walks a path (file or directory), runs `lint` plus the structural checks per file, and prints a report grouped by file. It is advisory: it always exits 0 and never edits anything.

## The hook (`hooks/`)

A `PostToolUse` hook matches `Write|Edit|MultiEdit` and runs `slop_lint_hook.py`. The hook reads the tool payload, lints the written file by extension, prints any tells to stderr, and always exits 0. It is warn-only by design: a design linter that blocks edits fights the author, so this one only informs. It also degrades safely, swallowing any internal error rather than interrupting your session.

## Commands and skills

Commands are Markdown prompts. They orchestrate the interactive and creative work (interviewing, generating the brandbook, tuning tokens, composing demo screens) and shell out to the scripts for the mechanical steps. They load skills for the judgment.

Skills are the durable know-how, kept separate from any one command so every command draws on the same standards:

- **`taste`** is loaded first for any UI work. It sets the Design Read, the three dials, the consistency locks, and the anti-slop tells.
- **`brand`** structures the brandbook into concrete, reference-backed content.
- **`tokens-and-system`** defines the token taxonomy, the source-of-truth discipline, and the `design.md` format.
- **`motion`** keeps animation motivated, cheap to render, and reduced-motion aware.
- **`unslop-copy`** removes AI-slop tells from prose in three passes.

## Data flow: what `/picasso:init` does

```
1. Ask for the folder name (default design-system).
2. picasso_scaffold.py  ->  copies templates + wires CLAUDE.md.
3. taste skill          ->  a one-line Design Read + the three dials.
4. brand + unslop-copy  ->  fills brandbook.md.
5. tokens-and-system    ->  tunes tokens.css, then fills design.md.
6. motion + taste       ->  composes the chosen demo screens.
7. picasso_review.py    ->  audits the result; anything flagged gets resolved.
8. Hand off             ->  open styleguide.html and brandbook.html to review.
```

The source of truth stays `tokens.css`; `styleguide.html` and the demo screens render from it, so reviewing the tokens reviews the whole system.

## Testing

Every engine function, script, and template ships with tests (`tests/`). The templates are guarded by tests proving they are self-contained, reference only defined tokens, and are free of the tells the plugin exists to remove. One end-to-end test scaffolds a fresh project and runs the reviewer against it, asserting zero findings, which proves the shipped defaults pass their own audit.
