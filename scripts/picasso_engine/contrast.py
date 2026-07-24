import re

_HEX = re.compile(r"^#([0-9a-fA-F]{3,8})$")
_RGB = re.compile(r"rgba?\(\s*([0-9.]+)[,\s]+([0-9.]+)[,\s]+([0-9.]+)", re.IGNORECASE)


def parse_color(value):
    """Return (r, g, b) 0-255 for a hex or rgb()/rgba() color, else None."""
    if not isinstance(value, str):
        return None
    v = value.strip()
    m = _HEX.match(v)
    if m:
        h = m.group(1)
        if len(h) in (3, 4):
            return tuple(int(h[i] * 2, 16) for i in range(3))
        if len(h) in (6, 8):
            return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16))
        return None
    m = _RGB.match(v)
    if m:
        return tuple(int(round(float(m.group(i)))) for i in (1, 2, 3))
    return None


def _channel(c):
    s = c / 255.0
    return s / 12.92 if s <= 0.03928 else ((s + 0.055) / 1.055) ** 2.4


def relative_luminance(rgb):
    r, g, b = rgb
    return 0.2126 * _channel(r) + 0.7152 * _channel(g) + 0.0722 * _channel(b)


def contrast_ratio(fg, bg):
    """WCAG contrast ratio between two colors, or None if either won't parse."""
    a, b = parse_color(fg), parse_color(bg)
    if a is None or b is None:
        return None
    la, lb = relative_luminance(a), relative_luminance(b)
    hi, lo = max(la, lb), min(la, lb)
    return (hi + 0.05) / (lo + 0.05)


def passes_aa(fg, bg, large=False):
    """True if the pair meets WCAG AA (3.0 large/UI, else 4.5). None if unparsable."""
    ratio = contrast_ratio(fg, bg)
    if ratio is None:
        return None
    return ratio >= (3.0 if large else 4.5)
