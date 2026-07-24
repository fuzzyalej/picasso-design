import re
import math
from dataclasses import dataclass

HEX = re.compile(r"#[0-9a-fA-F]{3,8}\b")
PURE_BLACK = re.compile(r"#000(?:000)?(?:ff|f)?\b", re.IGNORECASE)
DASH = re.compile(r"[\u2014\u2013]")  # em-dash, en-dash (unicode escapes; avoids literal chars in source)
CUSTOM_PROP_DECL_FULL = re.compile(r"--[A-Za-z0-9_-]+\s*:\s*[^;]*;?")
HTML_STYLE_ATTR = re.compile(r'style\s*=\s*(["\'])(.*?)\1', re.IGNORECASE | re.DOTALL)


@dataclass
class Finding:
    rule: str
    severity: str  # "warn" | "info"
    message: str
    line: int
    snippet: str


def _lines(content: str):
    return content.splitlines()


def _check_dash(content: str, kind: str):
    if kind == "css":
        return
    for i, line in enumerate(_lines(content), 1):
        if DASH.search(line):
            yield Finding("em-dash", "warn",
                          "Em/en dash in copy: replace with a comma, period, or reword.",
                          i, line.strip())


def _check_pure_black(content: str, kind: str):
    if kind == "copy":
        return
    for i, line in enumerate(_lines(content), 1):
        if PURE_BLACK.search(line):
            yield Finding("pure-black", "warn",
                          "Pure black (#000). Use an off-black token (e.g. zinc-950).",
                          i, line.strip())


def _check_inline_hex(content: str, kind: str):
    if kind == "css":
        for i, line in enumerate(_lines(content), 1):
            remainder = CUSTOM_PROP_DECL_FULL.sub("", line)
            if HEX.search(remainder):
                yield Finding("inline-hex", "warn",
                              "Raw hex in CSS. Reference a token via var(--...).",
                              i, line.strip())
    elif kind == "html":
        for i, line in enumerate(_lines(content), 1):
            for attr in HTML_STYLE_ATTR.finditer(line):
                if HEX.search(attr.group(2)):
                    yield Finding("inline-hex", "warn",
                                  "Raw hex in inline style. Reference a token via var(--...).",
                                  i, line.strip())


PURPLE_WORDS = re.compile(r"\b(purple|indigo|violet)\b", re.IGNORECASE)
PURPLE_HEX = re.compile(r"#(6366f1|7c3aed|8b5cf6|a855f7|818cf8|c084fc)\b", re.IGNORECASE)
GRADIENT_CALL = re.compile(r"(?:linear|radial|conic)-gradient\s*\(((?:[^()]|\([^()]*\))*)\)", re.IGNORECASE)
SECTION_TAG = re.compile(r"<section\b", re.IGNORECASE)
ALLCAPS_TEXT = re.compile(r">\s*([A-Z0-9][A-Z0-9 ·|/&]{4,})\s*<")
FAKE_METRIC = re.compile(
    r"(\+?\d[\d,]*\s?%\s*(?:conversion|growth|faster|increase|more))"
    r"|(trusted by\s+[\d,]+\+?)"
    r"|(\b\d[\d,]*\+?\s+(?:users|customers|teams|companies)\b)"
    r"|(\b9{2,3}(?:\.9+)?\s?%)",
    re.IGNORECASE,
)
GRID_COLS = re.compile(r"grid-template-columns\s*:\s*([^;}]+)", re.IGNORECASE)
CTA_TAG = re.compile(r"<(a|button)\b([^>]*)>(.*?)</\1>", re.IGNORECASE | re.DOTALL)
TAG_STRIP = re.compile(r"<[^>]+>")
CTA_CLASS = re.compile(r"class\s*=\s*[\"'][^\"']*(?:btn|cta|button)", re.IGNORECASE)
IMG_TAG = re.compile(r"<img\b([^>]*)>", re.IGNORECASE)
ALT_ATTR = re.compile(r"\balt\s*=", re.IGNORECASE)
OUTLINE_NONE = re.compile(r"outline\s*:\s*(?:none|0)\b", re.IGNORECASE)
FOCUS_VISIBLE = re.compile(r":focus-visible", re.IGNORECASE)
CLICKABLE_NONSEMANTIC = re.compile(r"<(?:div|span)\b[^>]*\bonclick\s*=[^>]*>", re.IGNORECASE)
ROLE_ATTR = re.compile(r"\brole\s*=", re.IGNORECASE)


def _check_purple_gradient(content: str, kind: str):
    if kind == "copy":
        return
    for i, line in enumerate(_lines(content), 1):
        for g in GRADIENT_CALL.finditer(line):
            body = g.group(1)
            if PURPLE_WORDS.search(body) or PURPLE_HEX.search(body):
                yield Finding("purple-gradient", "warn",
                              "Indigo/purple gradient: the #1 AI-slop tell. Pick a deliberate accent.",
                              i, line.strip())


def _check_eyebrow_overuse(content: str, kind: str):
    if kind != "html":
        return
    sections = max(1, len(SECTION_TAG.findall(content)))
    budget = math.ceil(sections / 3)
    eyebrows = ALLCAPS_TEXT.findall(content)
    if len(eyebrows) > budget:
        yield Finding("eyebrow-overuse", "info",
                      f"{len(eyebrows)} all-caps kickers for {sections} section(s) "
                      f"(budget {budget}). Cap eyebrows at 1 per 3 sections.",
                      1, eyebrows[0].strip())


def _check_fake_metric(content: str, kind: str):
    if kind == "css":
        return
    for i, line in enumerate(_lines(content), 1):
        m = FAKE_METRIC.search(line)
        if m:
            yield Finding("fake-metric", "warn",
                          "Looks like a fabricated metric. Use real numbers or remove.",
                          i, m.group(0).strip())


def _check_grid_1fr(content: str, kind: str):
    if kind == "copy":
        return
    for i, line in enumerate(_lines(content), 1):
        for m in GRID_COLS.finditer(line):
            value = m.group(1)
            if "1fr" in value.lower() and "minmax(0" not in value.replace(" ", ""):
                yield Finding("grid-1fr", "info",
                              "Grid uses 1fr; prefer minmax(0,1fr) so cells don't overflow.",
                              i, m.group(0).strip())


def _norm_cta(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip().lower()


def _check_duplicate_cta(content: str, kind: str):
    if kind != "html":
        return
    seen = {}
    for m in CTA_TAG.finditer(content):
        if not CTA_CLASS.search(m.group(2)):
            continue
        text = _norm_cta(TAG_STRIP.sub("", m.group(3)))
        if not text:
            continue
        seen[text] = seen.get(text, 0) + 1
    for text, count in seen.items():
        if count > 1:
            yield Finding("duplicate-cta", "info",
                          f"CTA '{text}' appears {count} times; one label per CTA intent.",
                          1, text)


def _check_img_alt(content: str, kind: str):
    if kind != "html":
        return
    for i, line in enumerate(_lines(content), 1):
        for m in IMG_TAG.finditer(line):
            if not ALT_ATTR.search(m.group(1)):
                yield Finding("img-alt", "warn",
                              'Image without alt. Add alt text, or alt="" if decorative.',
                              i, line.strip())


def _check_focus_removed(content: str, kind: str):
    if kind == "copy":
        return
    if FOCUS_VISIBLE.search(content):
        return
    for i, line in enumerate(_lines(content), 1):
        if OUTLINE_NONE.search(line):
            yield Finding("focus-removed", "warn",
                          "Focus outline removed with no :focus-visible replacement.",
                          i, line.strip())


def _check_clickable_nonsemantic(content: str, kind: str):
    if kind != "html":
        return
    for i, line in enumerate(_lines(content), 1):
        for m in CLICKABLE_NONSEMANTIC.finditer(line):
            if not ROLE_ATTR.search(m.group(0)):
                yield Finding("clickable-nonsemantic", "info",
                              "Clickable div/span without a role. Use a button/link, "
                              "or add role plus keyboard support.",
                              i, line.strip())


_CORE_RULES = [
    _check_dash, _check_pure_black, _check_inline_hex,
    _check_purple_gradient, _check_eyebrow_overuse, _check_fake_metric,
    _check_grid_1fr, _check_duplicate_cta,
    _check_img_alt, _check_focus_removed, _check_clickable_nonsemantic,
]


def lint(content: str, kind: str, tokens: dict | None = None) -> list:
    findings = []
    for rule in _CORE_RULES:
        findings.extend(rule(content, kind))
    return findings
