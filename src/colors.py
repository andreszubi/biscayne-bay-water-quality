"""WCAG 2.1 colour-contrast helpers.

Used by the charts (to pick readable label colours) and by the accessibility
tests (to check every colour pair in the light and dark themes).
"""
from plotly.colors import hex_to_rgb, unlabel_rgb

# WCAG 2.1 AA minimums.
TEXT_CONTRAST = 4.5  # normal-size text (1.4.3)
NON_TEXT_CONTRAST = 3.0  # chart marks, input borders, icons (1.4.11)


def _to_rgb(color: str) -> tuple[float, float, float]:
    """Accept '#RRGGBB' or 'rgb(r, g, b)' and return 0–255 channels."""
    return hex_to_rgb(color) if color.startswith("#") else unlabel_rgb(color)


def relative_luminance(color: str) -> float:
    """Relative luminance as defined by WCAG (0 = black, 1 = white)."""

    def channel(c: float) -> float:
        c /= 255
        return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4

    r, g, b = (channel(c) for c in _to_rgb(color))
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contrast_ratio(a: str, b: str) -> float:
    """WCAG contrast ratio between two colours, from 1 (none) to 21 (black on white)."""
    lighter, darker = sorted((relative_luminance(a), relative_luminance(b)), reverse=True)
    return (lighter + 0.05) / (darker + 0.05)


def readable_text_on(fill: str) -> str:
    """Black or white, whichever has more contrast against `fill`."""
    return "#000000" if contrast_ratio("#000000", fill) >= contrast_ratio("#FFFFFF", fill) else "#FFFFFF"
