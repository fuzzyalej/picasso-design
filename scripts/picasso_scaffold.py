#!/usr/bin/env python3
"""picasso scaffold: copy the design-system templates into a project and wire CLAUDE.md."""
import os
import shutil
import sys

sys.path.insert(0, os.path.dirname(__file__))
from picasso_engine.claude_md import upsert_managed_block  # noqa: E402

TEMPLATE_FILES = [
    "tokens.css",
    "styleguide.html",
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
        written.append(rel)
    return written


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


def main(argv=None):
    import argparse
    parser = argparse.ArgumentParser(prog="picasso-scaffold")
    parser.add_argument("--project", default=".")
    parser.add_argument("--dir", default="design-system", dest="folder")
    parser.add_argument("--templates", required=True)
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args(argv)
    written = scaffold(args.project, args.folder, args.templates, args.force)
    wire_claude_md(args.project, args.folder)
    print(f"picasso: wrote {len(written)} file(s) into {args.folder}/ and wired CLAUDE.md.")
    for rel in written:
        print(f"  + {args.folder}/{rel}")
    sys.exit(0)


if __name__ == "__main__":
    main()
