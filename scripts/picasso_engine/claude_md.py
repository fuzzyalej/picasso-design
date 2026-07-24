import re

START = "<!-- picasso:start -->"
END = "<!-- picasso:end -->"
# Greedy to the LAST END so a body that itself contains marker text still
# replaces cleanly (stays idempotent).
_BLOCK = re.compile(re.escape(START) + r".*" + re.escape(END), re.DOTALL)


def upsert_managed_block(existing: str, body: str) -> str:
    block = f"{START}\n{body}\n{END}"
    if START in existing and END in existing:
        # Function replacement avoids re interpreting backslashes in `block`.
        return _BLOCK.sub(lambda _m: block, existing, count=1)
    if existing.strip() == "":
        return block + "\n"
    return existing.rstrip("\n") + "\n\n" + block + "\n"
