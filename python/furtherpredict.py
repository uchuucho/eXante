import pandas as pd
import numpy as np

def forecast_with_scenario(forecast_file, metal_name, scenario,
                            G=0.0, P=0.0, M=0.0, beta=None, sheet_name=0):
    df = pd.read_excel(forecast_file, sheet_name=sheet_name)
    df.columns = df.columns.str.strip()
    if metal_name not in df.columns:
        raise ValueError(f"{metal_name} not found in file")

    df["P_base"] = pd.to_numeric(df[metal_name], errors="coerce")
    df = df.dropna(subset=["P_base"])
    beta = beta or {}

    active = {"G": 0, "P": 0, "M": 0}
    if   scenario == "-":  pass
    elif scenario == "G":  active["G"] = 1
    elif scenario == "P":  active["P"] = 1
    elif scenario == "M":  active["M"] = 1
    else: raise ValueError(f"Invalid scenario: {scenario}")

    shock = (
        active["G"] * beta.get("G", 0) * G +
        active["P"] * beta.get("P", 0) * P +
        active["M"] * beta.get("M", 0) * M
    )

    # Cap shock to prevent explosion: max ±40% price move per scenario
    shock = max(-0.51, min(0.51, shock))

    df["P_adjusted"] = df["P_base"] * np.exp(shock)
    return df[[df.columns[0], "P_base", "P_adjusted"]]