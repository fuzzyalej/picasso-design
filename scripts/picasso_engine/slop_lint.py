import sys
from dataclasses import dataclass

from picasso_engine.rules import load_rules
from picasso_engine.schemes import run_check


@dataclass
class Finding:
    rule: str
    severity: str  # "warn" | "info"
    message: str
    line: int
    snippet: str


def format_finding(f: Finding) -> str:
    """One report line for a finding, naming the offender via `snippet`
    when present (a token pair, an undefined token, an external URL)."""
    line = f"  [{f.severity}] {f.rule} (line {f.line}): {f.message}"
    if f.snippet:
        line += f" [{f.snippet}]"
    return line


def findings_for(criterion, content: str, kind: str, tokens=None) -> list:
    """Run one criterion's checks and build its findings."""
    if criterion.verification != "automated":
        return []
    out = []
    for check in criterion.checks:
        for line, snippet in run_check(check, content, kind, tokens):
            out.append(Finding(criterion.identifier, criterion.severity,
                               criterion.message or "", line, snippet))
    return out


def lint(content: str, kind: str, tokens: dict | None = None,
         rules: list | None = None) -> list:
    """Lint content of a given kind. Never raises."""
    findings = []
    try:
        criteria = rules if rules is not None else load_rules()[0]
        for criterion in criteria:
            findings.extend(findings_for(criterion, content, kind, tokens))
    except Exception as exc:  # warn-only: a broken rule set must never break the caller
        print(f"picasso: rule set error, rules not applied: {exc}", file=sys.stderr)
    findings.sort(key=lambda f: (f.line, f.rule))
    return findings
