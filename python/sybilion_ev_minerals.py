import os, json, time, tempfile
import pandas as pd
import numpy as np
import requests
from dotenv import load_dotenv
from decision import make_decision
from shock_model import load_betas
from furtherpredict import forecast_with_scenario

load_dotenv()

TOKEN = os.environ.get("SYBILION_API_TOKEN")
if not TOKEN:
    raise SystemExit("ERROR: Set SYBILION_API_TOKEN in .env")

BASE_URL = "https://api.sybilion.dev"
HEADERS  = {"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"}
CSV_FILE    = "../data/ev_minerals.csv"
OUTPUT_FILE = "../data/ev_minerals_results.json"
BETAS_FILE  = "../data/betas.json"

MINERALS = {
    "PLITH":    {"name":"Lithium (99% Battery Grade)","key":"lithium",  "unit":"EUR/ton","keywords":["lithium","battery","EV","electric vehicle","energy storage"]},
    "PCOBA":    {"name":"Cobalt",                     "key":"cobalt",   "unit":"USD/lb", "keywords":["cobalt","battery cathode","EV","DRC","mining"]},
    "PNICK":    {"name":"Nickel",                     "key":"nickel",   "unit":"USD/mt", "keywords":["nickel","NMC","EV","stainless steel","Indonesia"]},
    "PMANGELE": {"name":"Manganese",                  "key":"manganese","unit":"USD/mt", "keywords":["manganese","LFP","cathode","EV","steel","South Africa"]},
}

MINERAL_TO_BETA_KEY = {
    "lithium":"Lithium", "cobalt":"Cobalt", "nickel":"Nickel", "manganese":"Manganese"
}

def api_get(path):
    r = requests.get(f"{BASE_URL}{path}", headers={k:v for k,v in HEADERS.items() if k!="Content-Type"})
    r.raise_for_status(); return r.json()

def api_post(path, body):
    r = requests.post(f"{BASE_URL}{path}", headers=HEADERS, json=body)
    r.raise_for_status(); return r.json()

# ── Load CSV ──────────────────────────────────────────────────────────────────
print("📂 Loading CSV...")
df = pd.read_csv(CSV_FILE)
month_cols = [c for c in df.columns if len(c)==8 and "-M" in c]

def extract_timeseries(code):
    mask = (df["SERIES_CODE"].str.contains(code, na=False) &
            (df["OBS_MEASURE"]=="OBS_VALUE") &
            df["DATA_TRANSFORMATION"].str.contains("US dollars", na=False))
    rows = df[mask]
    if rows.empty: return None
    row = rows.iloc[0]
    ts  = {}
    for col in month_cols:
        val = row[col]
        if pd.notna(val):
            year, month = col.split("-M")
            ts[f"{year}-{month.zfill(2)}-01"] = round(float(val), 4)
    return ts

mineral_data = {}
for code, meta in MINERALS.items():
    ts = extract_timeseries(code)
    if ts:
        mineral_data[code] = {**meta, "timeseries": ts}
        vals  = list(ts.values())
        mineral_data[code]["history_values"] = vals[-6:] if len(vals) >= 6 else vals
        mineral_data[code]["history_dates"]  = sorted(ts.keys())[-6:]
        print(f"  ✅ {meta['name']}: {len(ts)} obs, last={vals[-1]:.2f}")
    else:
        print(f"  ⚠️  {meta['name']}: not found")
print()

# ── API auth ──────────────────────────────────────────────────────────────────
print("🔑 Verifying API key...")
me = api_get("/api/v1/me")
print(f"   User: {me.get('user_id')}  Balance: €{me.get('available_eur_cents',0)/100:.2f}\n")

# ── Submit forecasts ──────────────────────────────────────────────────────────
print("🚀 Submitting forecasts...")
job_ids = {}
for code, data in mineral_data.items():
    body = {
        "pipeline_version":"v1","frequency":"monthly","soft_horizon":6,"recency_factor":0.5,
        "timeseries_metadata":{"title":f"{data['name']} Monthly Price ({data['unit']})","description":f"Monthly commodity price for {data['name']}. Key EV battery material. Source: IMF.","keywords":data["keywords"]},
        "timeseries": data["timeseries"],
    }
    resp = api_post("/api/v1/forecasts", body)
    job_ids[code] = resp["job_id"]
    print(f"  {data['name']}: {resp['job_id']}")
print()

# ── Poll ──────────────────────────────────────────────────────────────────────
print("⏳ Waiting for forecasts...")
results, pending = {}, set(job_ids.keys())
while pending:
    for code in list(pending):
        sd = api_get(f"/api/v1/forecasts/{job_ids[code]}")
        if sd.get("settled"):
            print(f"  ✅ {mineral_data[code]['name']}: {sd.get('status')}")
            results[code] = sd; pending.remove(code)
        elif sd.get("status") == "failed":
            print(f"  ❌ {mineral_data[code]['name']}: FAILED")
            results[code] = sd; pending.remove(code)
    if pending: time.sleep(10)
print()

# ── Download artifacts ────────────────────────────────────────────────────────
all_output = {}
for code, sd in results.items():
    if sd.get("status") != "completed": continue
    entry = {"name":mineral_data[code]["name"],"key":mineral_data[code]["key"],"unit":mineral_data[code]["unit"],"job_id":job_ids[code]}
    try: entry["forecast"]         = api_get(f"/api/v1/forecasts/{job_ids[code]}/artifacts/forecast.json")
    except Exception as e: print(f"  ⚠️  forecast.json: {e}")
    try: entry["external_signals"] = api_get(f"/api/v1/forecasts/{job_ids[code]}/artifacts/external_signals.json")
    except Exception as e: print(f"  ⚠️  external_signals.json: {e}")
    all_output[code] = entry

# ── Drivers ───────────────────────────────────────────────────────────────────
print("🔍 Fetching drivers...")
for code, data in mineral_data.items():
    if code not in all_output: continue
    try:
        body = {"timeseries_metadata":{"title":data["name"],"description":f"Prices for {data['name']}","keywords":data["keywords"]},"timeseries":data["timeseries"]}
        all_output[code]["drivers"] = api_post("/api/v1/drivers", body)
        print(f"  ✅ {data['name']}")
    except Exception as e: print(f"  ⚠️  {data['name']}: {e}")

# ── Load YOUR OLS betas ───────────────────────────────────────────────────────
print("\n📐 Loading OLS betas...")
try:
    all_betas = load_betas(BETAS_FILE)
    print(f"✅ Loaded: {list(all_betas.keys())}")
except FileNotFoundError:
    raise SystemExit("\n❌ betas.json not found.\n   Run: python3 shock_model.py\n")

# ── Enrich: history, p50/p10/p90, betas, decision, scenario grid ──────────────
print("\n⚡ Computing decisions and scenarios...")
for code, entry in all_output.items():
    fc_series = entry.get("forecast",{}).get("data",{}).get("forecast_series",{})
    if not fc_series: continue

    dates = sorted(fc_series.keys())
    spot  = list(mineral_data[code]["timeseries"].values())[-1]
    p50   = [fc_series[d]["forecast"] for d in dates]
    p10   = [fc_series[d]["quantile_forecast"].get("0.10", fc_series[d]["forecast"]*0.92) for d in dates]
    p90   = [fc_series[d]["quantile_forecast"].get("0.90", fc_series[d]["forecast"]*1.10) for d in dates]

    entry["spot"]           = spot
    entry["forecast_dates"] = dates
    entry["p50_base"]       = p50
    entry["p10_base"]       = p10
    entry["p90_base"]       = p90
    entry["history_values"] = mineral_data[code]["history_values"]
    entry["history_dates"]  = mineral_data[code]["history_dates"]

    beta_key = MINERAL_TO_BETA_KEY.get(entry["key"], "")
    beta_raw = all_betas.get(beta_key, {})
    entry["beta"] = beta_raw

    if beta_raw:
        print(f"  ✅ {entry['name']} betas: G={beta_raw.get('G',0):.3f}, P={beta_raw.get('P',0):.3f}, M={beta_raw.get('M',0):.3f}")
    else:
        print(f"  ⚠️  No betas for {entry['key']} — check metals.xlsx sheet names match {list(MINERAL_TO_BETA_KEY.values())}")

    api_forecast = {d:{"mean":p50[i],"lower":p10[i],"upper":p90[i]} for i,d in enumerate(dates)}
    entry["decision_baseline"] = make_decision(api_forecast, spot, G=0, P=0, M=0, beta=beta_raw)

    # Scenario grid via furtherpredict.py with YOUR betas
    fc_df = pd.DataFrame({"date": dates, "price": p50})
    with tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False) as tmp:
        tmp_path = tmp.name
    fc_df.to_excel(tmp_path, index=False)

    grid = {}
    for scenario, G, P, M in [
        ("-",  0.0,  0.0,  0.0),
        ("G",  0.25, 0.0,  0.0),
        ("P",  0.0,  0.25, 0.0),
        ("M",  0.0,  0.0,  0.25),
    ]:
        key = f"G={G},P={P},M={M}"
        GP = G*P; GM = G*M; PM = P*M; GPM = G*P*M
        active = {"G":0,"P":0,"M":0}
        if   scenario == "-": pass
        elif scenario == "G": active["G"] = 1
        elif scenario == "P": active["P"] = 1
        elif scenario == "M": active["M"] = 1
        shock = (
            active["G"] * beta_raw.get("G", 0) * G +
            active["P"] * beta_raw.get("P", 0) * P +
            active["M"] * beta_raw.get("M", 0) * M
        )
        shock = max(-0.51, min(0.51, shock))
        grid[key] = [round(v * np.exp(shock), 4) for v in p50]
    entry["scenario_grid"] = grid

    os.unlink(tmp_path)
    entry["scenario_grid"] = grid
    print(f"  ✅ {entry['name']} — {entry['decision_baseline']['action']}")

# ── Save ──────────────────────────────────────────────────────────────────────
with open(OUTPUT_FILE, "w") as f:
    json.dump(all_output, f, indent=2)
print(f"\n💾 Saved to {OUTPUT_FILE}")