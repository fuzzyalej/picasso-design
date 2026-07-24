#!/usr/bin/env python3
"""picasso review: audit design artifacts for slop tells and drift."""
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from picasso_engine.slop_lint import lint, Finding  # noqa: E402
from picasso_engine.tokens import parse_tokens  # noqa: E402
from picasso_engine.artifact_check import external_deps, undefined_var_refs  # noqa: E402
from picasso_engine.kinds import kind_for, KIND_BY_EXT  # noqa: E402
from picasso_engine.contrast import passes_aa, contrast_ratio  # noqa: E402

DESIGN_EXTS = tuple(KIND_BY_EXT)

# Conventional foreground/background token pairs to audit for AA contrast.
# parse_tokens is last-wins, so overridden tokens resolve to their dark-mode value; light-only AA failures are not caught here.
CONVENTIONAL_PAIRS = [
    ("color-text", "color-bg"),
    ("color-text", "color-surface"),
    ("color-text-muted", "color-bg"),
    ("color-accent-contrast", "color-accent"),
]


def contrast_findings(tokens: dict) -> list:
    findings = []
    for fg, bg in CONVENTIONAL_PAIRS:
        if fg not in tokens or bg not in tokens:
            continue
        if passes_aa(tokens[fg], tokens[bg]) is False:
            ratio = contrast_ratio(tokens[fg], tokens[bg])
            findings.append(Finding(
                "contrast", "warn",
                f"--{fg} on --{bg} is {ratio:.1f}:1, below WCAG AA 4.5:1.",
                1, f"--{fg} / --{bg}"))
    return findings


def _read(path: str) -> str:
    with open(path, "r", encoding="utf-8") as fh:
        return fh.read()


def review_content(path: str, content: str, tokens: dict) -> list:
    kind = kind_for(path)
    if not kind:
        return []
    findings = list(lint(content, kind, tokens))
    if kind in ("html", "css"):
        for dep in external_deps(content):
            findings.append(Finding(
                "external-dep", "warn",
                f"External dependency '{dep}'. Artifacts must be self-contained; inline or vendor it.",
                1, dep))
        for ref in undefined_var_refs(content, tokens):
            findings.append(Finding(
                "undefined-token", "warn",
                f"Uses {ref}, which is not defined in tokens.css.",
                1, ref))
    return findings


def _iter_files(paths):
    for p in paths:
        if os.path.isdir(p):
            for root, _dirs, files in os.walk(p):
                for name in sorted(files):
                    if name.lower().endswith(DESIGN_EXTS):
                        yield os.path.join(root, name)
        elif os.path.isfile(p):
            yield p


def review_paths(paths, tokens_css_path=None):
    tokens = {}
    if tokens_css_path and os.path.isfile(tokens_css_path):
        try:
            tokens = parse_tokens(_read(tokens_css_path))
        except (OSError, UnicodeDecodeError):
            tokens = {}
    results = []
    for p in paths:
        if not os.path.exists(p):
            results.append((p, Finding(
                "missing-path", "warn",
                "Path not found; nothing was scanned here.", 1, p)))
    seen = set()
    for f in _iter_files(paths):
        key = os.path.abspath(f)
        if key in seen:
            continue
        seen.add(key)
        try:
            content = _read(f)
        except (OSError, UnicodeDecodeError):
            continue
        for finding in review_content(f, content, tokens):
            results.append((f, finding))
    if tokens:
        anchor = tokens_css_path or "tokens.css"
        for finding in contrast_findings(tokens):
            results.append((anchor, finding))
    return results


def format_report(results) -> str:
    if not results:
        return "picasso: no slop tells found. The design system looks clean."
    by_file = {}
    for path, finding in results:
        by_file.setdefault(path, []).append(finding)
    out = [f"picasso: {len(results)} finding(s) across {len(by_file)} file(s):"]
    for path, findings in by_file.items():
        out.append("")
        out.append(path)
        for f in findings:
            out.append(f"  [{f.severity}] {f.rule} (line {f.line}): {f.message}")
    return "\n".join(out)


def _default_tokens_path(paths):
    for p in paths:
        cand = os.path.join(p, "tokens.css") if os.path.isdir(p) else None
        if cand and os.path.isfile(cand):
            return cand
    if os.path.isfile("design-system/tokens.css"):
        return "design-system/tokens.css"
    return None


def main(argv=None):
    import argparse
    parser = argparse.ArgumentParser(prog="picasso-review")
    parser.add_argument("paths", nargs="*")
    parser.add_argument("--tokens", default=None)
    args = parser.parse_args(argv)
    paths = args.paths or ["design-system"]
    tokens_path = args.tokens or _default_tokens_path(paths)
    results = review_paths(paths, tokens_path)
    print(format_report(results))
    sys.exit(0)


if __name__ == "__main__":
    main()
