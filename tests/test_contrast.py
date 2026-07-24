from picasso_engine.contrast import (
    parse_color, contrast_ratio, passes_aa,
)


def test_parse_hex_forms():
    assert parse_color("#fff") == (255, 255, 255)
    assert parse_color("#ffffff") == (255, 255, 255)
    assert parse_color("#18181b") == (24, 24, 27)
    assert parse_color("#18181bff") == (24, 24, 27)  # alpha ignored


def test_parse_rgb_and_bad_input():
    assert parse_color("rgb(37, 99, 235)") == (37, 99, 235)
    assert parse_color("rgba(37,99,235,0.5)") == (37, 99, 235)
    assert parse_color("var(--x)") is None
    assert parse_color(None) is None


def test_contrast_ratio_extremes():
    assert round(contrast_ratio("#000000", "#ffffff"), 1) == 21.0
    assert round(contrast_ratio("#ffffff", "#ffffff"), 1) == 1.0
    assert contrast_ratio("var(--a)", "#fff") is None


def test_passes_aa():
    assert passes_aa("#ffffff", "#2563eb") is True   # ~5.2:1
    assert passes_aa("#777777", "#ffffff") is False  # ~4.5 boundary fails
    assert passes_aa("#767676", "#ffffff", large=True) is True
    assert passes_aa("var(--x)", "#fff") is None
