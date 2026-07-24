import re

ATTR_URL = re.compile(
    r"""(?:src|href)\s*=\s*(?:"([^"]*)"|'([^']*)'|([^\s>]+))""", re.IGNORECASE
)
CSS_URL = re.compile(
    r"""url\(\s*(?:"([^"]*)"|'([^']*)'|([^)]*))\)""", re.IGNORECASE
)
IMPORT_REF = re.compile(r"""@import\s+(?:url\(\s*)?["']([^"']+)["']""", re.IGNORECASE)
SRCSET = re.compile(r"""srcset\s*=\s*(?:"([^"]*)"|'([^']*)')""", re.IGNORECASE)
EXTERNAL_VALUE = re.compile(r"^\s*(?:https?:)?//", re.IGNORECASE)
VAR_REF = re.compile(r"var\(\s*(--[A-Za-z0-9_-]+)")


def _external(value: str) -> bool:
    return bool(value) and bool(EXTERNAL_VALUE.match(value))


def external_deps(content: str) -> list:
    hits = []
    for regex in (ATTR_URL, CSS_URL):
        for m in regex.finditer(content):
            value = (m.group(1) or m.group(2) or m.group(3) or "").strip()
            if _external(value) and value not in hits:
                hits.append(value)
    for m in IMPORT_REF.finditer(content):
        value = m.group(1).strip()
        if _external(value) and value not in hits:
            hits.append(value)
    for m in SRCSET.finditer(content):
        raw = (m.group(1) or m.group(2) or "").strip()
        for candidate in raw.split(","):
            candidate = candidate.strip()
            if not candidate:
                continue
            url = candidate.split()[0]
            if _external(url) and url not in hits:
                hits.append(url)
    return hits


def undefined_var_refs(content: str, tokens: dict) -> list:
    defined = {"--" + name for name in tokens}
    missing = []
    for m in VAR_REF.finditer(content):
        name = m.group(1)
        if name not in defined and name not in missing:
            missing.append(name)
    return missing
