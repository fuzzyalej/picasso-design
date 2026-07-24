import os

KIND_BY_EXT = {".html": "html", ".htm": "html", ".css": "css", ".md": "copy"}


def kind_for(path: str):
    """Return the lint kind for a path's extension, or None if unhandled."""
    return KIND_BY_EXT.get(os.path.splitext(path.lower())[1])
