"""Criterion model, validation, and loading for picasso's rule layer."""
import json
import os
import re
from dataclasses import dataclass, field

from picasso_engine.schemes import BUILTINS

RULES_VERSION = "1"

LEVELS = ("must", "must-not", "should", "should-not")
CATEGORIES = (
    "visual-design", "interaction", "accessibility",
    "content", "motion", "development",
)
VERIFICATIONS = ("automated", "assisted", "manual")
SCHEMES = ("regex", "token-pair", "builtin")
KINDS = ("html", "css", "copy")

_REQUIRED = ("identifier", "title", "statement", "level", "category", "verification")
_OPTIONAL = (
    "message", "check", "rationale", "evidence", "references",
    "target", "examples", "disabled",
)
_ALLOWED = set(_REQUIRED) | set(_OPTIONAL)

_IDENTIFIER = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


@dataclass
class Criterion:
    identifier: str
    title: str = ""
    statement: str = ""
    level: str = "must-not"
    category: str = "visual-design"
    verification: str = "automated"
    message: str | None = None
    checks: list = field(default_factory=list)
    rationale: str | None = None
    evidence: str | None = None
    references: list = field(default_factory=list)
    target: str | None = None
    examples: list = field(default_factory=list)
    disabled: bool = False

    @property
    def severity(self) -> str:
        return severity_for(self.level)


def severity_for(level: str) -> str:
    return "warn" if level in ("must", "must-not") else "info"


def _normalize_prose(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", (text or "").lower()).strip()


def _as_checks(rule: dict) -> list:
    check = rule.get("check")
    if check is None:
        return []
    return list(check) if isinstance(check, list) else [check]


def _validate_kinds(check, scheme: str, where: str, errors: list) -> None:
    """Both content-driven schemes declare the kinds they apply to, so a rule's
    reach is readable from the JSON alone."""
    kinds = check.get("kinds")
    if not kinds or not all(k in KINDS for k in kinds):
        errors.append(f"{where}: {scheme} check needs kinds drawn from {KINDS}")


def _validate_pattern(value, label: str, where: str, errors: list) -> None:
    try:
        re.compile(value)
    except re.error as exc:
        errors.append(f"{where}: {label} ({exc})")


def _validate_regex_check(check, where: str, errors: list) -> None:
    _validate_kinds(check, "regex", where, errors)
    if "pattern" not in check:
        errors.append(f"{where}: regex check needs a pattern")
    for key in ("pattern", "skipIfFileMatches", "absent"):
        if check.get(key) is not None:
            _validate_pattern(check[key], f"{key} is not a valid pattern", where, errors)
    for stripped in check.get("strip") or []:
        _validate_pattern(stripped, "strip pattern invalid", where, errors)
    within = check.get("within")
    if within is None:
        return
    if not isinstance(within, dict) or "pattern" not in within:
        errors.append(f"{where}: within needs a pattern and an optional group")
    else:
        _validate_pattern(within["pattern"], "within pattern invalid", where, errors)


def _validate_token_pair_check(check, where: str, errors: list) -> None:
    pairs = check.get("pairs")
    if not pairs or not all(
        isinstance(p, (list, tuple)) and len(p) == 2 for p in pairs
    ):
        errors.append(f"{where}: token-pair needs pairs of two token names")


def _validate_builtin_check(check, where: str, errors: list, builtin_names) -> None:
    name = check.get("name")
    if builtin_names is not None and name not in builtin_names:
        errors.append(f"{where}: unknown builtin name {name!r}")
    _validate_kinds(check, "builtin", where, errors)


def _validate_check(check, where: str, errors: list, builtin_names) -> None:
    if not isinstance(check, dict):
        errors.append(f"{where}: check must be an object or a list of objects")
        return
    scheme = check.get("scheme")
    if scheme == "regex":
        _validate_regex_check(check, where, errors)
    elif scheme == "token-pair":
        _validate_token_pair_check(check, where, errors)
    elif scheme == "builtin":
        _validate_builtin_check(check, where, errors, builtin_names)
    else:
        errors.append(f"{where}: unknown scheme {scheme!r}; expected one of {SCHEMES}")


def _validate_scheme_mix(checks, where: str, errors: list) -> None:
    """token-pair evaluates the token map, not content; mixing it with a
    content-driven scheme on the same rule is incoherent."""
    schemes = {c.get("scheme") for c in checks if isinstance(c, dict)}
    if "token-pair" in schemes and len(schemes) > 1:
        errors.append(
            f"{where}: token-pair cannot be combined with other schemes "
            "on the same rule (token-pair evaluates tokens, not content)")


def validate_rules(raw, allow_disabled: bool = False) -> list:
    """Return a list of human-readable errors; empty means valid."""
    errors = []
    if not isinstance(raw, dict):
        return ["rules file must be a JSON object"]
    version = raw.get("picassoRulesVersion")
    if version != RULES_VERSION:
        errors.append(
            f"unsupported picassoRulesVersion {version!r}; expected {RULES_VERSION!r}")
    rules = raw.get("rules")
    if not isinstance(rules, list):
        return errors + ["rules must be a list"]

    builtin_names = set(BUILTINS)

    seen = set()
    for index, rule in enumerate(rules):
        where = f"rule {index}"
        if not isinstance(rule, dict):
            errors.append(f"{where}: must be an object")
            continue
        identifier = rule.get("identifier")
        if identifier:
            where = f"rule {identifier!r}"
        if not identifier or not _IDENTIFIER.match(str(identifier)):
            errors.append(f"{where}: identifier must be kebab-case")
        elif identifier in seen:
            errors.append(f"{where}: duplicate identifier")
        else:
            seen.add(identifier)

        unknown = set(rule) - _ALLOWED
        if unknown:
            errors.append(f"{where}: unknown field(s) {sorted(unknown)}")

        if rule.get("disabled"):
            if not allow_disabled:
                errors.append(
                    f"{where}: disabled is only allowed in a project rules file")
            continue

        for key in _REQUIRED:
            if not rule.get(key):
                errors.append(f"{where}: missing required field {key!r}")

        level = rule.get("level")
        if level is not None and level not in LEVELS:
            errors.append(f"{where}: level must be one of {LEVELS}")
        category = rule.get("category")
        if category is not None and category not in CATEGORIES:
            errors.append(f"{where}: category must be one of {CATEGORIES}")
        verification = rule.get("verification")
        if verification is not None and verification not in VERIFICATIONS:
            errors.append(f"{where}: verification must be one of {VERIFICATIONS}")

        checks = _as_checks(rule)
        _validate_scheme_mix(checks, where, errors)
        automated = verification == "automated"
        if automated:
            if not checks:
                errors.append(f"{where}: an automated rule needs a check")
            if not rule.get("message"):
                errors.append(f"{where}: an automated rule needs a message")
            outcomes = {e.get("outcome") for e in rule.get("examples") or []}
            if "pass" not in outcomes or "fail" not in outcomes:
                errors.append(
                    f"{where}: needs at least one pass example and one fail example")
        elif checks:
            errors.append(
                f"{where}: check is not allowed on a {verification!r} rule")

        for check in checks:
            _validate_check(check, where, errors, builtin_names)

        rationale = rule.get("rationale")
        if rationale and _normalize_prose(rationale) == _normalize_prose(
                rule.get("statement", "")):
            errors.append(f"{where}: rationale must not restate the statement")

    return errors


def criteria_from(raw) -> list:
    """Build Criterion objects from already-validated raw data."""
    out = []
    for rule in raw.get("rules") or []:
        out.append(Criterion(
            identifier=rule.get("identifier", ""),
            title=rule.get("title", ""),
            statement=rule.get("statement", ""),
            level=rule.get("level", "must-not"),
            category=rule.get("category", "visual-design"),
            verification=rule.get("verification", "automated"),
            message=rule.get("message"),
            checks=_as_checks(rule),
            rationale=rule.get("rationale"),
            evidence=rule.get("evidence"),
            references=rule.get("references") or [],
            target=rule.get("target"),
            examples=rule.get("examples") or [],
            disabled=bool(rule.get("disabled")),
        ))
    return out


# Repository layout: this file is scripts/picasso_engine/rules.py,
# so the shipped rule set is two directories up.
_ENGINE_DIR = os.path.dirname(os.path.abspath(__file__))
CORE_PATH = os.path.join(os.path.dirname(os.path.dirname(_ENGINE_DIR)),
                         "rules", "core.json")

PROJECT_RULES_FILENAME = "rules.json"
_MAX_WALK_UP = 6


def load_raw(path: str):
    """Read and parse a rules file. Returns (raw, errors)."""
    if not path or not os.path.isfile(path):
        return None, [f"rules file not found: {path}"]
    try:
        with open(path, "r", encoding="utf-8") as fh:
            return json.load(fh), []
    except (OSError, UnicodeDecodeError) as exc:
        return None, [f"could not read {path}: {exc}"]
    except json.JSONDecodeError as exc:
        return None, [f"could not parse {path}: {exc}"]


def merge(core: list, project: list) -> list:
    """Merge project criteria over core: override, append, or disable."""
    result = list(core)
    index = {c.identifier: i for i, c in enumerate(result)}
    for criterion in project:
        position = index.get(criterion.identifier)
        if criterion.disabled:
            if position is not None:
                result[position] = None
            continue
        if position is None:
            index[criterion.identifier] = len(result)
            result.append(criterion)
        else:
            result[position] = criterion
    return [c for c in result if c is not None]


def find_project_rules(start_path: str):
    """Walk up from a file looking for a sibling project rules.json."""
    if not start_path:
        return None
    directory = os.path.dirname(os.path.abspath(start_path))
    for _ in range(_MAX_WALK_UP):
        candidate = os.path.join(directory, PROJECT_RULES_FILENAME)
        if os.path.isfile(candidate):
            return candidate
        parent = os.path.dirname(directory)
        if parent == directory:
            break
        directory = parent
    return None


def load_rules(project_path: str | None = None):
    """Load core rules, optionally merged with a project file.

    Returns (criteria, errors). Errors never prevent a usable return value:
    a broken project file degrades to core-only.
    """
    errors = []
    core_raw, core_errors = load_raw(CORE_PATH)
    core = []
    if core_raw is None:
        errors.extend(f"core.json: {e}" for e in core_errors)
    else:
        core_problems = validate_rules(core_raw)
        if core_problems:
            errors.extend(f"core.json: {e}" for e in core_problems)
        else:
            core = criteria_from(core_raw)

    if not project_path:
        return core, errors

    name = os.path.basename(project_path)
    project_raw, project_errors = load_raw(project_path)
    if project_raw is None:
        return core, errors + [f"{name}: {e}" for e in project_errors]
    project_problems = validate_rules(project_raw, allow_disabled=True)
    if project_problems:
        return core, errors + [f"{name}: {e}" for e in project_problems]
    return merge(core, criteria_from(project_raw)), errors


PLUGIN_VERSION = "0.4.0"

EMPTY_PROJECT_RULES = {
    "picassoRulesVersion": RULES_VERSION,
    "rules": [],
}


def stamp_for(kind: str) -> str:
    """A one-line provenance comment for a generated artifact."""
    text = f"picasso {PLUGIN_VERSION} · rules v{RULES_VERSION}"
    if kind == "css":
        return f"/* {text} */"
    return f"<!-- {text} -->"
