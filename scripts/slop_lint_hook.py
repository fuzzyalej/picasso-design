#!/usr/bin/env python3
"""Warn-only PostToolUse hook: lint written design files for slop tells."""
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__)))
from picasso_engine.slop_lint import lint  # noqa: E402
from picasso_engine.kinds import kind_for  # noqa: E402


def run(payload: dict) -> str:
    tool_input = payload.get("tool_input", {}) or {}
    path = tool_input.get("file_path", "")
    kind = kind_for(path)
    if not kind:
        return ""
    content = tool_input.get("content")
    if content is None:
        try:
            with open(path, "r", encoding="utf-8") as fh:
                content = fh.read()
        except (OSError, UnicodeDecodeError):
            return ""
    if not isinstance(content, str):
        return ""
    findings = lint(content, kind)
    if not findings:
        return ""
    header = f"picasso: {len(findings)} slop tell(s) in {os.path.basename(path)}:"
    body = "\n".join(
        f"  [{f.severity}] {f.rule} (line {f.line}): {f.message}" for f in findings
    )
    return f"{header}\n{body}"


def main():
    try:
        payload = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        sys.exit(0)
    try:
        message = run(payload)
    except Exception:
        sys.exit(0)  # warn-only: never block, even on an internal error
    if message:
        print(message, file=sys.stderr)
    sys.exit(0)


if __name__ == "__main__":
    main()
