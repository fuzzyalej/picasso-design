import re

DEFAULT_NAME = "picasso"


def markers(name: str = DEFAULT_NAME):
    return f"<!-- {name}:start -->", f"<!-- {name}:end -->"


# Kept for backward compatibility with existing callers and tests.
START, END = markers()


def _block_re(start: str, end: str):
    # Greedy to the LAST end marker so a body containing marker text still
    # replaces cleanly (stays idempotent).
    return re.compile(re.escape(start) + r".*" + re.escape(end), re.DOTALL)


def upsert_managed_block(existing: str, body: str,
                         name: str = DEFAULT_NAME) -> str:
    prefix = name if name == DEFAULT_NAME else f"{DEFAULT_NAME}:{name}"
    start, end = markers(prefix)
    block = f"{start}\n{body}\n{end}"
    if start in existing and end in existing:
        # Function replacement avoids re interpreting backslashes in `block`.
        return _block_re(start, end).sub(lambda _m: block, existing, count=1)
    if existing.strip() == "":
        return block + "\n"
    return existing.rstrip("\n") + "\n\n" + block + "\n"


def extract_managed_block(existing: str, name: str = DEFAULT_NAME):
    """Return the body inside a named block, or None if absent."""
    prefix = name if name == DEFAULT_NAME else f"{DEFAULT_NAME}:{name}"
    start, end = markers(prefix)
    match = _block_re(start, end).search(existing)
    if not match:
        return None
    inner = match.group(0)[len(start):-len(end)]
    return inner.strip("\n")
