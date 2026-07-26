#!/usr/bin/env python3
"""picasso scaffold: copy the design-system templates into a project and wire CLAUDE.md."""
import json
import os
import shutil
import sys

sys.path.insert(0, os.path.dirname(__file__))
from picasso_engine.claude_md import upsert_managed_block  # noqa: E402
from picasso_engine.kinds import kind_for  # noqa: E402
from picasso_engine.rules import (  # noqa: E402
    EMPTY_PROJECT_RULES, find_project_rules, load_rules, stamp_for,
)
from picasso_engine.rules_render import render_all  # noqa: E402

TEMPLATE_FILES = [
    "tokens.css",
    "components.css",
    "design_system.html",
    "brandbook.html",
    "design.md",
    "brandbook.md",
    "design-instructions.md",
    "demo/landing.html",
]


def scaffold(project_dir, folder_name, templates_dir, force=False):
    written = []
    base = os.path.join(project_dir, folder_name)
    for rel in TEMPLATE_FILES:
        src = os.path.join(templates_dir, rel)
        dest = os.path.join(base, rel)
        if os.path.exists(dest) and not force:
            continue
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        shutil.copyfile(src, dest)
        _stamp(dest)
        written.append(rel)
    if write_empty_rules(base, force):
        written.append("rules.json")
    if "design.md" in written:
        _render_design_md(os.path.join(base, "design.md"))
    return written


def _stamp(path: str) -> None:
    """Append a one-line provenance comment to a freshly written artifact,
    as its own last line. Only ever called right after a fresh copy, so a
    single call always produces a single stamp."""
    kind = kind_for(path)
    if kind is None:
        return
    with open(path, "r", encoding="utf-8") as fh:
        content = fh.read()
    prefix = content if content.endswith("\n") else content + "\n"
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(prefix + stamp_for(kind) + "\n")


def write_empty_rules(base: str, force: bool = False) -> bool:
    """Create an empty project rules file. Returns True if written."""
    path = os.path.join(base, "rules.json")
    if os.path.exists(path) and not force:
        return False
    os.makedirs(base, exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(EMPTY_PROJECT_RULES, fh, indent=2)
        fh.write("\n")
    return True


def _render_design_md(design_md_path):
    """Fill design.md's rule blocks from the merged (core + project) rule
    set so a fresh scaffold starts in sync (nothing to flag as stale on the
    first review)."""
    render_design_md(design_md_path)


def render_design_md(design_md_path, project_rules_path=None):
    """Re-render an existing design.md's managed rule blocks in place from
    the current merged rule set. Does nothing else: no template copying, no
    CLAUDE.md wiring, no rules.json write. Returns True if the content
    changed.

    This is the only supported way to close the drift loop `rules-stale`
    reports: hand-editing rules.json and then re-rendering, without
    `--force` overwriting the rest of the document from the template.
    """
    if project_rules_path is None:
        project_rules_path = find_project_rules(design_md_path)
    criteria, _errors = load_rules(project_rules_path)
    with open(design_md_path, "r", encoding="utf-8") as fh:
        existing = fh.read()
    rendered = render_all(existing, criteria)
    changed = rendered != existing
    with open(design_md_path, "w", encoding="utf-8") as fh:
        fh.write(rendered)
    return changed


def instructions_block(folder_name: str) -> str:
    return (
        "## Design system\n\n"
        "This project uses the picasso design framework. Follow "
        f"`{folder_name}/design-instructions.md` for all UI and copy work. "
        f"`{folder_name}/tokens.css` is the source of truth for design values."
    )


def wire_claude_md(project_dir, folder_name):
    path = os.path.join(project_dir, "CLAUDE.md")
    existing = ""
    if os.path.isfile(path):
        with open(path, "r", encoding="utf-8") as fh:
            existing = fh.read()
    updated = upsert_managed_block(existing, instructions_block(folder_name))
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(updated)
    return path


def wire_gitignore(project_dir, folder_name):
    path = os.path.join(project_dir, ".gitignore")
    entry = f"{folder_name}/.picasso/"
    existing = ""
    if os.path.isfile(path):
        with open(path, "r", encoding="utf-8") as fh:
            existing = fh.read()
    lines = existing.splitlines()
    if entry not in lines:
        prefix = existing if existing.endswith("\n") or existing == "" else existing + "\n"
        existing = prefix + entry + "\n"
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(existing)
    return path


def main(argv=None):
    import argparse
    parser = argparse.ArgumentParser(prog="picasso-scaffold")
    parser.add_argument("--project", default=".")
    parser.add_argument("--dir", default="design-system", dest="folder")
    parser.add_argument("--templates", default=None)
    parser.add_argument("--force", action="store_true")
    parser.add_argument(
        "--render", action="store_true",
        help="Re-render an existing design.md's managed rule blocks in "
             "place, then exit. No template copying, no CLAUDE.md wiring, "
             "no rules.json write.")
    args = parser.parse_args(argv)

    if args.render:
        design_md_path = os.path.join(args.project, args.folder, "design.md")
        if not os.path.isfile(design_md_path):
            print(f"picasso: no design.md at {args.folder}/design.md; nothing to render.")
            sys.exit(1)
        changed = render_design_md(design_md_path)
        if changed:
            print(f"picasso: re-rendered {args.folder}/design.md's managed rule blocks.")
        else:
            print(f"picasso: {args.folder}/design.md's managed rule blocks were already in sync.")
        sys.exit(0)

    if not args.templates:
        parser.error("--templates is required unless --render is given")

    written = scaffold(args.project, args.folder, args.templates, args.force)
    wire_claude_md(args.project, args.folder)
    wire_gitignore(args.project, args.folder)
    print(f"picasso: wrote {len(written)} file(s) into {args.folder}/ and wired CLAUDE.md.")
    for rel in written:
        print(f"  + {args.folder}/{rel}")
    sys.exit(0)


if __name__ == "__main__":
    main()
