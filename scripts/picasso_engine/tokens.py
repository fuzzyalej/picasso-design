import re

_CUSTOM_PROP = re.compile(r"--([A-Za-z0-9_-]+)\s*:\s*([^;]+);")


def parse_tokens(css: str) -> dict:
    """Return {name-without-dashes: value} for every CSS custom property."""
    return {m.group(1): m.group(2).strip() for m in _CUSTOM_PROP.finditer(css)}
