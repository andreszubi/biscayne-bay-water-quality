"""WCAG 2.1 colour-contrast helpers and colour banding for the maps.

Used by the charts (to pick readable label colours), by both maps (to split
values into clearly different shades) and by the accessibility tests (to
check every colour pair in the light and dark themes).
"""
import numpy as np
import pandas as pd
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


def shade_bands(values: pd.Series, shades: list[str]) -> tuple[pd.Series, list[float], list[str]]:
    """Split values into equal-count bands, one shade per band.

    Readings cluster around typical values, so a smooth gradient would paint
    most of them in near-identical middle shades. Equal-count bands use every
    shade about equally, which makes low and high values easy to tell apart.

    Returns each value's band number (0 = lowest), the band edges, and the
    shade for each band (spread across the scale when there are fewer bands
    than shades, e.g. for a parameter with few distinct values).
    """
    if values.nunique() < 2:
        return pd.Series(0, index=values.index), [float(values.min()), float(values.max())], [shades[len(shades) // 2]]
    codes, edges = pd.qcut(values, q=len(shades), labels=False, retbins=True, duplicates="drop")
    n_bands = len(edges) - 1
    picks = np.linspace(0, len(shades) - 1, n_bands).round().astype(int)
    return codes.astype(int), [float(e) for e in edges], [shades[i] for i in picks]
