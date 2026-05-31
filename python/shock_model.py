import json
import pandas as pd
import numpy as np
import statsmodels.api as sm

METALS_FILE = "../data/metals.xlsx"
BETAS_FILE  = "../data/betas.json"

def fit_all(file=METALS_FILE):
    xls     = pd.ExcelFile(file)
    results = {}
    for sheet in xls.sheet_names:
        df = pd.read_excel(xls, sheet_name=sheet)
        df.columns = df.columns.str.strip()
        price_col = df.columns[1]
        y = np.log(pd.to_numeric(df[price_col], errors="coerce"))
        df = df[y.notna()].copy()
        y  = y[y.notna()]

        required = ["G", "P", "M"]
        missing  = [c for c in required if c not in df.columns]
        if missing:
            print(f"  ⚠️  {sheet}: missing columns {missing}, skipping")
            continue

        X     = sm.add_constant(df[required])
        model = sm.OLS(y, X).fit()

        # Cap betas at ±1.5 to prevent explosion
        params = model.params.to_dict()
        for k in ["G", "P", "M"]:
            if k in params:
                params[k] = max(-1.5, min(1.5, params[k]))

        results[price_col] = params
        print(f"  ✅ {price_col}: R²={model.rsquared:.3f}")
        print(f"     G={params.get('G',0):.3f}  P={params.get('P',0):.3f}  M={params.get('M',0):.3f}")

    return results

def save_betas(betas, path=BETAS_FILE):
    with open(path, "w") as f:
        json.dump(betas, f, indent=2)
    print(f"\n💾 Betas saved to {path}")

def load_betas(path=BETAS_FILE):
    with open(path) as f:
        return json.load(f)

if __name__ == "__main__":
    print("📐 Fitting shock regression models...\n")
    betas = fit_all()
    save_betas(betas)
    print("\nBeta summary:")
    print(pd.DataFrame(betas).T[["G","P","M"]].to_string())