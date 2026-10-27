"""Plain-language findings computed from whatever data the user has filtered.

Because the text is generated from the filtered DataFrame, the Insights
section updates as the sidebar filters change.
"""
import itertools

import pandas as pd

from src.config import (
    CORE_PARAMETERS,
    DEPTH_ZONE_COL,
    DO_STRESS_MG_L,
    HEALTHY_PH_RANGE,
    OCEAN_SALINITY_PPT,
    OPTICAL_PARAMETERS,
)
from src.data_loader import survey_duration_min, track_distance_m

# Pairs that measure the same physical quantity; their correlation is trivially ~1.
_REDUNDANT_PAIRS = {
    frozenset({"Salinity (ppt)", "Specific Conductance (mS/cm)"}),
    frozenset({"Dissolved Oxygen (mg/L)", "DO Saturation (%)"}),
}


def _strength(r: float) -> str:
    r = abs(r)
    if r >= 0.7:
        return "strong"
    if r >= 0.4:
        return "moderate"
    if r >= 0.2:
        return "weak"
    return "negligible"


def strongest_correlation(df: pd.DataFrame, parameters: list[str]) -> tuple[str, str, float] | None:
    """Most correlated pair of parameters, skipping pairs that measure the same thing."""
    corr = df[parameters].corr()
    best = None
    for a, b in itertools.combinations(parameters, 2):
        r = corr.loc[a, b]
        if frozenset({a, b}) in _REDUNDANT_PAIRS or pd.isna(r):
            continue
        if best is None or abs(r) > abs(best[2]):
            best = (a, b, float(r))
    return best


def generate_insights(df: pd.DataFrame) -> list[str]:
    """Return a list of Markdown bullet strings describing the filtered data."""
    if df.empty:
        return []

    insights = []
    temp = df["Temperature (°C)"]
    sal = df["Salinity (ppt)"]
    do = df["Dissolved Oxygen (mg/L)"]
    ph = df["pH"]
    depth = df["Water Depth (m)"]

    insights.append(
        f"**Survey coverage:** {len(df):,} readings collected over "
        f"{survey_duration_min(df):.1f} minutes along a {track_distance_m(df):,.0f} m track, "
        f"in water {depth.min():.1f}–{depth.max():.1f} m deep."
    )

    insights.append(
        f"**Temperature is very stable** ({temp.min():.2f}–{temp.max():.2f} °C, a spread of "
        f"{temp.max() - temp.min():.2f} °C), which suggests the water in this part of the bay is well mixed."
    )

    above_ocean = (sal > OCEAN_SALINITY_PPT).mean() * 100
    insights.append(
        f"**Salinity averages {sal.mean():.1f} ppt**, and {above_ocean:.0f}% of readings are above typical "
        f"open-ocean salinity ({OCEAN_SALINITY_PPT:.0f} ppt). Shallow lagoons like Biscayne Bay can become "
        f"saltier than the ocean during the dry season, when evaporation exceeds freshwater inflow."
    )

    low_do = (do < DO_STRESS_MG_L).mean() * 100
    do_status = (
        "no readings fall below" if low_do == 0 else f"{low_do:.1f}% of readings fall below"
    )
    insights.append(
        f"**Dissolved oxygen averages {do.mean():.2f} mg/L** (min {do.min():.2f}); {do_status} the "
        f"{DO_STRESS_MG_L:.0f} mg/L level where marine life starts to become stressed."
    )

    lo, hi = HEALTHY_PH_RANGE
    ph_note = "inside" if lo <= ph.mean() <= hi else "slightly outside"
    insights.append(
        f"**pH averages {ph.mean():.2f}**, {ph_note} the typical seawater range of {lo}–{hi}."
    )

    if df[DEPTH_ZONE_COL].nunique() > 1:
        r = depth.corr(do)
        direction = "higher" if r > 0 else "lower"
        insights.append(
            f"**Depth vs. oxygen:** there is a {_strength(r)} relationship (r = {r:.2f}) between water depth "
            f"and dissolved oxygen — deeper spots tend to have {direction} oxygen in this sample."
        )

    pair = strongest_correlation(df, list(CORE_PARAMETERS))
    if pair:
        a, b, r = pair
        sign = "positive" if r > 0 else "negative"
        insights.append(
            f"**Strongest relationship:** {a} and {b} show a {_strength(r)} {sign} correlation (r = {r:.2f}). "
            f"Explore it in the *Visualizations → Relationships* chart."
        )

    negative_share = {name: (df[name] < 0).mean() * 100 for name in OPTICAL_PARAMETERS}
    worst = max(negative_share, key=negative_share.get)
    insights.append(
        f"**Data quality note:** the optical sensors report physically impossible negative values "
        f"(e.g. {negative_share[worst]:.0f}% of {worst} readings), so they were likely not calibrated. "
        f"They are hidden by default; treat them as relative trends only."
    )
    return insights
