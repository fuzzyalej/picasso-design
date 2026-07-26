"""Execution of check schemes. Pure functions over content; no file I/O,
except `component_use_cases`, which reads a sibling components.css file
alongside the design.md content it is given. That is why the conformance
runner (tests/test_rules_conformance.py) exempts that one criterion: it
needs a project directory, not a single document."""
import math
import os
import re

from picasso_engine.artifact_check import external_deps, undefined_var_refs
from picasso_engine.contrast import contrast_ratio
from picasso_engine.tokens import PATH_KEY

BUILTINS = {}

# Regex-execution concern: compiling a check's flag string into re flags.
# Lives here (not in rules.py) because it is about running a check, not
# about loading or validating the rule model.
_FLAG_BY_LETTER = {"i": re.IGNORECASE, "s": re.DOTALL, "m": re.MULTILINE}


def compile_flags(flags: str):
    value = 0
    for letter in flags or "":
        value |= _FLAG_BY_LETTER.get(letter, 0)
    return value


def _compile(pattern, flags=""):
    return re.compile(pattern, compile_flags(flags))


def _run_regex(check, content, kind, tokens):
    if kind not in (check.get("kinds") or ()):
        return []
    flags = check.get("flags", "")
    guard = check.get("skipIfFileMatches")
    if guard and _compile(guard, flags).search(content):
        return []
    pattern = _compile(check["pattern"], flags)
    absent = _compile(check["absent"], flags) if check.get("absent") else None
    strips = [_compile(s, flags) for s in check.get("strip") or []]
    within = check.get("within")
    within_re = _compile(within["pattern"], flags) if within else None
    within_group = (within or {}).get("group", 1)

    hits = []
    for number, line in enumerate(content.splitlines(), 1):
        haystacks = [line]
        for stripped in strips:
            haystacks = [stripped.sub("", h) for h in haystacks]
        if within_re is not None:
            haystacks = [
                m.group(within_group) or ""
                for h in haystacks for m in within_re.finditer(h)
            ]
        for haystack in haystacks:
            match = pattern.search(haystack)
            if not match:
                continue
            if absent is not None and absent.search(match.group(0)):
                continue
            hits.append((number, line.strip()))
            break
    return hits


def run_check(check, content, kind, tokens=None):
    """Execute one check, returning (line_number, snippet) pairs."""
    scheme = check.get("scheme")
    if scheme == "regex":
        return _run_regex(check, content, kind, tokens)
    if scheme == "builtin":
        # Kinds gate builtins exactly as they gate regex checks, so a rule's
        # applicable kinds are readable from the JSON alone.
        if kind not in (check.get("kinds") or ()):
            return []
        function = BUILTINS.get(check.get("name"))
        if function is None:
            return []
        return list(function(content, kind, tokens))
    if scheme == "token-pair":
        return _run_token_pair(check, tokens)
    return []


PURPLE_WORDS = re.compile(r"\b(purple|indigo|violet)\b", re.IGNORECASE)
PURPLE_HEX = re.compile(
    r"#(6366f1|7c3aed|8b5cf6|a855f7|818cf8|c084fc)\b", re.IGNORECASE)
GRADIENT_CALL = re.compile(
    r"(?:linear|radial|conic)-gradient\s*\(((?:[^()]|\([^()]*\))*)\)", re.IGNORECASE)
SECTION_TAG = re.compile(r"<section\b", re.IGNORECASE)
ALLCAPS_TEXT = re.compile(r">\s*([A-Z0-9][A-Z0-9 \u00b7|/&]{4,})\s*<")
GRID_COLS = re.compile(r"grid-template-columns\s*:\s*([^;}]+)", re.IGNORECASE)
CTA_TAG = re.compile(r"<(a|button)\b([^>]*)>(.*?)</\1>", re.IGNORECASE | re.DOTALL)
TAG_STRIP = re.compile(r"<[^>]+>")
CTA_CLASS = re.compile(r"class\s*=\s*[\"'][^\"']*(?:btn|cta|button)", re.IGNORECASE)


def purple_gradient(content, kind, tokens=None):
    for number, line in enumerate(content.splitlines(), 1):
        for gradient in GRADIENT_CALL.finditer(line):
            body = gradient.group(1)
            if PURPLE_WORDS.search(body) or PURPLE_HEX.search(body):
                yield number, line.strip()
                break


def eyebrow_overuse(content, kind, tokens=None):
    sections = max(1, len(SECTION_TAG.findall(content)))
    budget = math.ceil(sections / 3)
    eyebrows = ALLCAPS_TEXT.findall(content)
    if len(eyebrows) > budget:
        yield 1, eyebrows[0].strip()


def grid_1fr(content, kind, tokens=None):
    for number, line in enumerate(content.splitlines(), 1):
        for match in GRID_COLS.finditer(line):
            value = match.group(1)
            if "1fr" in value.lower() and "minmax(0" not in value.replace(" ", ""):
                yield number, match.group(0).strip()


def duplicate_cta(content, kind, tokens=None):
    seen = {}
    for match in CTA_TAG.finditer(content):
        if not CTA_CLASS.search(match.group(2)):
            continue
        text = re.sub(r"\s+", " ", TAG_STRIP.sub("", match.group(3))).strip().lower()
        if not text:
            continue
        seen[text] = seen.get(text, 0) + 1
    for text, count in seen.items():
        if count > 1:
            yield 1, text


BUILTINS.update({
    "purple_gradient": purple_gradient,
    "eyebrow_overuse": eyebrow_overuse,
    "grid_1fr": grid_1fr,
    "duplicate_cta": duplicate_cta,
})


def _run_token_pair(check, tokens):
    if tokens is None:
        return []
    minimum = check.get("minRatio", 4.5)
    hits = []
    for foreground, background in check.get("pairs") or []:
        if foreground not in tokens or background not in tokens:
            continue
        ratio = contrast_ratio(tokens[foreground], tokens[background])
        if ratio is not None and ratio < minimum:
            hits.append((1, f"--{foreground} / --{background} at {ratio:.1f}:1"))
    return hits


def external_deps_check(content, kind, tokens=None):
    for dependency in external_deps(content):
        yield 1, dependency


def undefined_token_refs(content, kind, tokens=None):
    if tokens is None:
        return
    for reference in undefined_var_refs(content, tokens):
        yield 1, reference


BUILTINS.update({
    "external_deps_check": external_deps_check,
    "undefined_token_refs": undefined_token_refs,
})


CLASS_SELECTOR = re.compile(r"^\.([a-z][a-z0-9]*(?:-[a-z0-9]+)*)")
_NOT_A_COMPONENT = ("is", "has", "sr", "visually")


def class_families(css: str) -> list:
    """Base component class names declared in a stylesheet."""
    families = []
    for line in css.splitlines():
        for segment in line.split("{", 1)[0].split(","):
            match = CLASS_SELECTOR.match(segment.strip())
            if not match:
                continue
            base = match.group(1).split("--")[0].split("__")[0]
            if base.split("-")[0] in _NOT_A_COMPONENT:
                continue
            if base not in families:
                families.append(base)
    return families


BULLET = re.compile(r"^\s*-\s")
NOT_FOR = re.compile(r"not for:", re.IGNORECASE)


def _bullet_groups(content: str) -> list:
    """Split markdown into bullet groups: a '- ' line plus its indented continuations."""
    groups = []
    current = None
    for line in content.splitlines():
        if BULLET.match(line):
            if current is not None:
                groups.append(current)
            current = [line]
        elif current is not None and line.strip():
            current.append(line)
        elif current is not None:
            groups.append(current)
            current = None
    if current is not None:
        groups.append(current)
    return ["\n".join(group) for group in groups]


def component_use_cases(content, kind, tokens=None):
    """Flag components in components.css with no 'Not for:' line in design.md.

    Reads a sibling file (components.css) rather than acting on `content`
    alone, unlike every other builtin in this module. That is why the
    conformance runner in tests/test_rules_conformance.py exempts this
    criterion's examples: that runner supplies a single self-contained
    document, and this check needs a project directory.
    """
    if not tokens:
        return
    design_path = tokens.get(PATH_KEY)
    if not design_path or os.path.basename(design_path) != "design.md":
        return
    stylesheet = os.path.join(os.path.dirname(design_path), "components.css")
    if not os.path.isfile(stylesheet):
        return
    try:
        with open(stylesheet, "r", encoding="utf-8") as fh:
            css = fh.read()
    except (OSError, UnicodeDecodeError):
        return
    groups = _bullet_groups(content)
    for family in class_families(css):
        if not _family_documented(family, groups):
            yield 1, family


def _family_documented(family: str, groups: list) -> bool:
    """A family is documented by a group that names it (as a base class,
    not merely as a Not-for target) before that group's 'Not for:' line."""
    marker = re.compile(r"\." + re.escape(family) + r"(?![\w-])")
    for group in groups:
        not_for = NOT_FOR.search(group)
        if not_for and marker.search(group[:not_for.start()]):
            return True
    return False


BUILTINS["component_use_cases"] = component_use_cases
