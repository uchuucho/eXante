"""
scenario_forecast.py — Applies G/P/M shock sliders to a baseline forecast.
Used by sybilion_ev_minerals.py after fetching Sybilion forecasts.

The frontend sends slider values G, P, M ∈ [0, 1].
This module computes the log-linear adjustment and returns adjusted prices.

Model:
    log(P_adjusted) = log(P_base) + β_G·G + β_P·P + β_M·M
                    + β_GP·G·P + β_GM·G·M + β_PM·P·M + β_GPM·G·P·M

    P_adjusted = P_base · exp(shock)

Scenario shortcuts (for pre-computation):
    "-"   : no shock
    "G"   : geopolitical only
    "P"   : policy only
    "M"   : mining only
    "GP"  : geo + policy
    "GM"  : geo + mining
    "PM"  : policy + mining
    "GPM" : all three
"""

import numpy as np
import pandas as pd


SCENARIO_ACTIVE = {
    "-":   {"G": 0, "P": 0, "M": 0, "GP": 0, "GM": 0, "PM": 0, "GPM": 0},
    "G":   {"G": 1, "P": 0, "M": 0, "GP": 0, "GM": 0, "PM": 0, "GPM": 0},
    "P":   {"G": 0, "P": 1, "M": 0, "GP": 0, "GM": 0, "PM": 0, "GPM": 0},
    "M":   {"G": 0, "P": 0, "M": 1, "GP": 0, "GM": 0, "PM": 0, "GPM": 0},
    "GP":  {"G": 1, "P": 1, "M": 0, "GP": 1, "GM": 0, "PM": 0, "GPM": 0},
    "GM":  {"G": 1, "P": 0, "M": 1, "GP": 0, "GM": 1, "PM": 0, "GPM": 0},
    "PM":  {"G": 0, "P": 1, "M": 1, "GP": 0, "GM": 0, "PM": 1, "GPM": 0},
    "GPM": {"G": 1, "P": 1, "M": 1, "GP": 1, "GM": 1, "PM": 1, "GPM": 1},
}


def compute_shock(G, P, M, beta):
    """
    Compute the log-scale shock for given slider values and fitted betas.

    Args:
        G, P, M : float  — slider values ∈ [0, 1]
        beta    : dict   — fitted OLS coefficients for this metal

    Returns:
        float : shock value (add to log price → multiply base price by exp(shock))
    """
    GP  = G * P
    GM  = G * M
    PM  = P * M
    GPM = G * P * M

    shock = (
        beta.get("G",   0) * G   +
        beta.get("P",   0) * P   +
        beta.get("M",   0) * M   +
        beta.get("GP",  0) * GP  +
        beta.get("GM",  0) * GM  +
        beta.get("PM",  0) * PM  +
        beta.get("GPM", 0) * GPM
    )
    return shock


def apply_scenario(baseline_forecast, G, P, M, beta):
    """
    Apply continuous G/P/M slider values to a baseline forecast series.

    Args:
        baseline_forecast : list[float] — p50 values (6 months)
        G, P, M           : float       — slider values ∈ [0, 1]
        beta              : dict        — fitted betas for this metal

    Returns:
        list[float] : adjusted forecast
    """
    shock = compute_shock(G, P, M, beta)
    return [round(p * np.exp(shock), 4) for p in baseline_forecast]


def apply_scenario_named(baseline_forecast, scenario, G, P, M, beta):
    """
    Apply a named scenario shortcut with given intensities.

    Args:
        baseline_forecast : list[float]
        scenario          : str  — one of SCENARIO_ACTIVE keys
        G, P, M           : float
        beta              : dict

    Returns:
        list[float] : adjusted forecast
    """
    if scenario not in SCENARIO_ACTIVE:
        raise ValueError(f"Unknown scenario '{scenario}'. Use: {list(SCENARIO_ACTIVE)}")

    active = SCENARIO_ACTIVE[scenario]
    GP  = G * P
    GM  = G * M
    PM  = P * M
    GPM = G * P * M

    shock = (
        active["G"]   * beta.get("G",   0) * G   +
        active["P"]   * beta.get("P",   0) * P   +
        active["M"]   * beta.get("M",   0) * M   +
        active["GP"]  * beta.get("GP",  0) * GP  +
        active["GM"]  * beta.get("GM",  0) * GM  +
        active["PM"]  * beta.get("PM",  0) * PM  +
        active["GPM"] * beta.get("GPM", 0) * GPM
    )

    return [round(p * np.exp(shock), 4) for p in baseline_forecast]


def precompute_scenario_grid(baseline_forecast, beta, steps=5):
    """
    Pre-compute adjusted forecasts across a grid of G/P/M values.
    Useful for caching scenario results before sending to the frontend.

    Args:
        baseline_forecast : list[float]
        beta              : dict
        steps             : int — number of steps per slider (default 5 → 0, 0.25, 0.5, 0.75, 1.0)

    Returns:
        dict : { "G=0.5,P=0.0,M=0.0": [p1, p2, ...], ... }
    """
    grid   = {}
    values = [round(i / (steps - 1), 2) for i in range(steps)]

    for g in values:
        for p in values:
            for m in values:
                key = f"G={g},P={p},M={m}"
                grid[key] = apply_scenario(baseline_forecast, g, p, m, beta)

    return grid


if __name__ == "__main__":
    # Smoke test
    baseline = [14200, 14900, 15600, 16191, 16700, 17100]
    beta     = {"const": 9.5, "G": -0.08, "P": -0.04, "M": -0.05,
                "GP": -0.02, "GM": -0.01, "PM": -0.01}

    print("Baseline:      ", baseline)
    print("G=0.5:         ", apply_scenario(baseline, G=0.5, P=0.0, M=0.0, beta=beta))
    print("G=1.0, P=1.0:  ", apply_scenario(baseline, G=1.0, P=1.0, M=0.0, beta=beta))
    print("GPM full:      ", apply_scenario(baseline, G=1.0, P=1.0, M=1.0, beta=beta))
