---
description: Audit this project's design artifacts and copy against tokens.css and the brandbook, and report slop tells.
argument-hint: "[path ...]"
---

Audit the project's design system for AI-slop tells and drift.

Determine the design-system folder: use `design-system` by default, or the folder named in the picasso block of `CLAUDE.md` if a different one was chosen at init.

Run:
`python3 "${CLAUDE_PLUGIN_ROOT}/scripts/picasso_review.py" $ARGUMENTS`

If no path is given in `$ARGUMENTS`, pass the design-system folder explicitly (for example `<folder> --tokens <folder>/tokens.css`). The script otherwise defaults to `design-system/` and uses `design-system/tokens.css` for token checks.

Present the report grouped by file. For each finding, explain briefly why it matters and propose a concrete fix that uses the project's tokens and brandbook. Do NOT change any files automatically; wait for the user to choose what to fix. If the report is clean, say so plainly.
