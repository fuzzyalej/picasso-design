#!/usr/bin/env python3
"""picasso review: audit design artifacts for slop tells and drift."""
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from picasso_engine.slop_lint import lint, Finding, findings_for, format_finding  # noqa: E402
from picasso_engine.tokens import parse_tokens, PATH_KEY  # noqa: E402
from picasso_engine.kinds import kind_for, KIND_BY_EXT  # noqa: E402
from picasso_engine.rules import load_rules, find_project_rules, CORE_PATH  # noqa: E402
from picasso_engine.rules_render import stale_blocks  # noqa: E402

DESIGN_EXTS = tuple(KIND_BY_EXT)


def _read(path: str) -> str:
    with open(path, "r", encoding="utf-8") as fh:
        return fh.read()


def review_content(path, content, tokens, rules=None):
    kind = kind_for(path)
    if not kind:
        return []
    return list(lint(content, kind, tokens, rules))


def _iter_files(paths):
    for p in paths:
        if os.path.isdir(p):
            for root, _dirs, files in os.walk(p):
                for name in sorted(files):
                    if name.lower().endswith(DESIGN_EXTS):
                        yield os.path.join(root, name)
        elif os.path.isfile(p):
            yield p


def _rule_set_findings(rule_errors, project_rules_path):
    """One finding per broken file, attributed correctly, with a count
    instead of one finding per validation error."""
    core_errors = [e for e in rule_errors if e.startswith("core.json:")]
    other_errors = [e for e in rule_errors if not e.startswith("core.json:")]
    findings = []
    if core_errors:
        findings.append((CORE_PATH, Finding(
            "rules-invalid", "warn",
            f"Rule set problem: {len(core_errors)} error(s) in core.json; "
            "the shipped rules were not applied.",
            1, core_errors[0])))
    if other_errors:
        path = project_rules_path or "rules.json"
        findings.append((path, Finding(
            "rules-invalid", "warn",
            f"Rule set problem: {len(other_errors)} error(s) in "
            f"{os.path.basename(path)}; falling back to the shipped rules.",
            1, other_errors[0])))
    return findings


def _stale_design_md_findings(paths, rules):
    findings = []
    for p in paths:
        design_md = os.path.join(p, "design.md") if os.path.isdir(p) else None
        if not design_md or not os.path.isfile(design_md):
            continue
        try:
            existing = _read(design_md)
        except (OSError, UnicodeDecodeError):
            continue
        for block in stale_blocks(existing, rules):
            findings.append((design_md, Finding(
                "rules-stale", "info",
                f"The '{block}' block no longer matches rules.json. "
                f"Re-render it, or move the edit into rules.json.",
                1, block)))
    return findings


def review_paths(paths, tokens_css_path=None, project_rules_path=None):
    tokens = {}
    if tokens_css_path and os.path.isfile(tokens_css_path):
        try:
            tokens = parse_tokens(_read(tokens_css_path))
        except (OSError, UnicodeDecodeError):
            tokens = {}

    rules, rule_errors = load_rules(project_rules_path)

    # token-pair checks run against the token map, not file content; keep them
    # out of the per-file pass so they don't fire once per scanned file.
    def _is_token_pair(criterion):
        return any(chk.get("scheme") == "token-pair" for chk in criterion.checks)

    token_pair_rules = [c for c in rules if _is_token_pair(c)]
    file_rules = [c for c in rules if not _is_token_pair(c)]

    results = []
    results.extend(_rule_set_findings(rule_errors, project_rules_path))
    for p in paths:
        if not os.path.exists(p):
            results.append((p, Finding(
                "missing-path", "warn",
                "Path not found; nothing was scanned here.", 1, p)))
    results.extend(_stale_design_md_findings(paths, rules))
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
        file_tokens = dict(tokens)
        file_tokens[PATH_KEY] = f
        for finding in review_content(f, content, file_tokens, file_rules):
            results.append((f, finding))

    # The token-pair scheme needs no file content; run it once, anchored at tokens.css.
    if tokens:
        anchor = tokens_css_path or "tokens.css"
        for criterion in token_pair_rules:
            for finding in findings_for(criterion, "", "css", tokens):
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
            out.append(format_finding(f))
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
    parser.add_argument("--rules", default=None)
    args = parser.parse_args(argv)
    paths = args.paths or ["design-system"]
    tokens_path = args.tokens or _default_tokens_path(paths)
    rules_path = args.rules
    if rules_path is None:
        rules_path = find_project_rules(tokens_path or (paths[0] + "/x"))
    results = review_paths(paths, tokens_path, rules_path)
    print(format_report(results))
    sys.exit(0)


if __name__ == "__main__":
    main()
