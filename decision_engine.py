"""
decision_engine.py — Threshold-based buy/hold/wait recommendation for eXante.

INPUT:
    mineral_key   : str         — "lithium" | "cobalt" | "manganese" | "nickel"
    spot_price    : float       — current market price
    forecast_p50  : list[float] — 6-month p50
    forecast_p10  : list[float] — 6-month p10 (downside)
    forecast_p90  : list[float] — 6-month p90 (upside)
    G, P, M       : float       — active slider values (for description text)

OUTPUT:
    dict:
        action  : str   — "Buy now" | "Buy partial" | "Hold" | "Wait"
        sub     : str   — one-line subtitle
        pct     : int   — 0–100 conviction score (drives ring fill in UI)
        color   : str   — CSS variable
        desc    : str   — narrative shown in UI card
"""

# ── Thresholds — tune these ───────────────────────────────────────────────────
THRESHOLDS = {
    # Min expected upside (p50 6m vs spot) to consider buying
    "min_upside_pct": 8.0,

    # p90-p10 spread as % of spot above this = high uncertainty
    "high_uncertainty_pct": 20.0,

    # Strong upside + low uncertainty → full buy
    "strong_buy_upside_pct": 15.0,

    # Forecast below spot by this % → wait / downtrend
    "downtrend_threshold_pct": -2.0,
}

ACTION_COLORS = {
    "Buy now":     "var(--accent)",
    "Buy partial": "var(--accent)",
    "Hold":        "var(--amber)",
    "Wait":        "var(--red)",
}


def compute_recommendation(mineral_key, spot_price, forecast_p50,
                            forecast_p10, forecast_p90, G=0.0, P=0.0, M=0.0):
    """
    Derive a buy/hold/wait recommendation from thresholds.

    Returns:
        dict { action, sub, pct, color, desc }
    """
    t = THRESHOLDS

    horizon_p50 = forecast_p50[-1]
    horizon_p10 = forecast_p10[-1]
    horizon_p90 = forecast_p90[-1]

    upside_pct  = ((horizon_p50 - spot_price) / spot_price) * 100
    spread_pct  = ((horizon_p90 - horizon_p10) / spot_price) * 100
    high_uncert = spread_pct > t["high_uncertainty_pct"]

    # Shock intensity for conviction penalty (0 = no shock, 1 = full GPM)
    shock_intensity = (G + P + M) / 3.0

    # ── Decision tree ─────────────────────────────────────────────────────────
    if upside_pct < t["downtrend_threshold_pct"]:
        action          = "Wait"
        sub             = "Downtrend in progress"
        base_conviction = 20

    elif upside_pct >= t["strong_buy_upside_pct"] and not high_uncert:
        action          = "Buy now"
        sub             = "Full allocation"
        base_conviction = 90

    elif upside_pct >= t["min_upside_pct"] and high_uncert:
        action          = "Buy partial"
        sub             = "Split across time"
        base_conviction = 65

    elif upside_pct >= t["min_upside_pct"] and not high_uncert:
        action          = "Buy partial"
        sub             = "Good entry point"
        base_conviction = 75

    else:
        action          = "Hold"
        sub             = "Wait for better entry"
        base_conviction = 35

    # Shock erodes conviction proportionally
    conviction = max(5, round(base_conviction * (1 - shock_intensity * 0.35)))

    desc = _build_description(
        action, mineral_key, upside_pct, spread_pct, G, P, M, high_uncert
    )

    return {
        "action": action,
        "sub":    sub,
        "pct":    conviction,
        "color":  ACTION_COLORS.get(action, "var(--accent)"),
        "desc":   desc,
    }


def _build_description(action, mineral, upside_pct, spread_pct, G, P, M, high_uncert):
    active_shocks = []
    if G > 0.1: active_shocks.append(f"geopolitical ({G:.0%})")
    if P > 0.1: active_shocks.append(f"policy ({P:.0%})")
    if M > 0.1: active_shocks.append(f"mining ({M:.0%})")

    shock_str  = f" Active shocks: {', '.join(active_shocks)}." if active_shocks else ""
    uncert_str = (" Uncertainty band is wide — stagger purchases."
                  if high_uncert else " Confidence interval is tight.")

    if action == "Buy now":
        return (f"{mineral.capitalize()} shows {upside_pct:.1f}% expected upside over 6 months."
                f"{uncert_str} Act before the window closes.{shock_str}")
    elif action == "Buy partial":
        return (f"{upside_pct:.1f}% expected upside with a {spread_pct:.0f}% p10–p90 spread."
                f"{uncert_str} Split coverage reduces timing risk.{shock_str}")
    elif action == "Hold":
        return (f"Upside is limited at {upside_pct:.1f}%. Hold current stock "
                f"and revisit in 4–6 weeks.{shock_str}")
    else:
        return (f"Forecast median is below spot ({upside_pct:.1f}%). "
                f"Downward pressure expected. Wait for a clearer floor.{shock_str}")


if __name__ == "__main__":
    rec = compute_recommendation(
        mineral_key  = "lithium",
        spot_price   = 14200,
        forecast_p50 = [14200, 14900, 15600, 16191, 16700, 17100],
        forecast_p10 = [13600, 13900, 14100, 14591, 14700, 14900],
        forecast_p90 = [14800, 15900, 16800, 17791, 18200, 18800],
        G=0.5, P=0.0, M=0.3,
    )
    print(rec)
