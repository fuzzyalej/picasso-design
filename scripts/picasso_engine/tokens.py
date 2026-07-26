import re

_CUSTOM_PROP = re.compile(r"--([A-Za-z0-9_-]+)\s*:\s*([^;]+);")

# Sentinel key threaded through the tokens dict to tell component_use_cases
# which design.md is being reviewed. The dot puts it outside _CUSTOM_PROP's
# character class, so a CSS declaration can never parse into this exact
# name (unlike the old "__path__", which the regex's underscore support let
# `--__path__: ...;` collide with by accident).
PATH_KEY = "__picasso.path__"


def parse_tokens(css: str) -> dict:
    """Return {name-without-dashes: value} for every CSS custom property."""
    return {m.group(1): m.group(2).strip() for m in _CUSTOM_PROP.finditer(css)}
