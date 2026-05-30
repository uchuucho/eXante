"""
Sybilion API - EV Minerals Forecast + Drivers
Lithium, Cobalt, Nickel, Manganese

Requirements:
    pip install requests pandas python-dotenv

Usage:
    python sybilion_ev_minerals.py
"""

import os
import json
import time
import pandas as pd
import requests
from dotenv import load_dotenv

load_dotenv()

# ── Config ────────────────────────────────────────────────────────────────────

TOKEN = os.environ.get("SYBILION_API_TOKEN")
if not TOKEN:
    raise SystemExit("ERROR: Set SYBILION_API_TOKEN in your .env file.\n"
                     "  SYBILION_API_TOKEN=sk_ops_...")

BASE_URL = "https://api.sybilion.dev"
HEADERS = {"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"}

CSV_FILE = "ev_minerals.csv"

# Which minerals to forecast (maps indicator keyword → friendly name + keywords)
MINERALS = {
    "PLITH":    {
        "name": "Lithium (99% Battery Grade)",
        "unit": "USD per tonne",
        "keywords": ["lithium", "battery", "EV", "electric vehicle", "energy storage", "anode"],
    },
    "PCOBA":    {
        "name": "Cobalt",
        "unit": "USD per pound",
        "keywords": ["cobalt", "battery cathode", "EV", "electric vehicle", "DRC", "mining"],
    },
    "PNICK":    {
        "name": "Nickel",
        "unit": "USD per metric tonne",
        "keywords": ["nickel", "battery cathode", "NMC", "EV", "stainless steel", "Indonesia"],
    },
    "PMANGELE": {
        "name": "Manganese",
        "unit": "USD per metric tonne",
        "keywords": ["manganese", "battery", "LFP", "cathode", "EV", "steel", "South Africa"],
    },
}


# ── Helper: make an authorized GET/POST ──────────────────────────────────────

def api_get(path):
    r = requests.get(f"{BASE_URL}{path}", headers={k: v for k, v in HEADERS.items() if k != "Content-Type"})
    r.raise_for_status()
    return r.json()

def api_post(path, body):
    r = requests.post(f"{BASE_URL}{path}", headers=HEADERS, json=body)
    r.raise_for_status()
    return r.json()

def api_get_raw(path):
    r = requests.get(f"{BASE_URL}{path}", headers={k: v for k, v in HEADERS.items() if k != "Content-Type"})
    r.raise_for_status()
    return r.json()


# ── Step 1: Load CSV ──────────────────────────────────────────────────────────

print("📂 Loading CSV...")
df = pd.read_csv(CSV_FILE)

# Month columns look like "2017-M01"
month_cols = [c for c in df.columns if len(c) == 8 and "-M" in c]

def extract_timeseries(series_code_fragment):
    """Pull the USD OBS_VALUE row for a given mineral code fragment."""
    mask = (
        df["SERIES_CODE"].str.contains(series_code_fragment, na=False) &
        (df["OBS_MEASURE"] == "OBS_VALUE") &
        df["DATA_TRANSFORMATION"].str.contains("US dollars", na=False)
    )
    rows = df[mask]
    if rows.empty:
        return None, None
    row = rows.iloc[0]
    indicator = row["INDICATOR"]
    ts = {}
    for col in month_cols:
        val = row[col]
        if pd.notna(val):
            year, month = col.split("-M")
            ts[f"{year}-{month.zfill(2)}-01"] = round(float(val), 4)
    return ts, indicator

# Parse all 4 minerals
mineral_data = {}
for code, meta in MINERALS.items():
    ts, indicator = extract_timeseries(code)
    if ts:
        mineral_data[code] = {**meta, "timeseries": ts, "indicator": indicator}
        print(f"  ✅ {meta['name']}: {len(ts)} observations  "
              f"({min(ts)} → {max(ts)})")
    else:
        print(f"  ⚠️  {meta['name']}: not found in CSV, skipping")

print()


# ── Step 2: Verify API auth ───────────────────────────────────────────────────

print("🔑 Verifying API key...")
me = api_get("/api/v1/me")
balance = me.get("available_eur_cents", 0)
print(f"   User:    {me.get('user_id')}")
print(f"   Balance: €{balance / 100:.2f}  (tier {me.get('api_usage_tier')})")
if balance < 10:
    print("⚠️  Low balance — you may need to top up before submitting forecasts.")
print()


# ── Step 3: Submit all forecasts ──────────────────────────────────────────────

job_ids = {}   # code → job_id

for code, data in mineral_data.items():
    print(f"🚀 Submitting forecast: {data['name']}...")
    body = {
        "pipeline_version": "v1",
        "frequency": "monthly",
        "soft_horizon": 6,
        "recency_factor": 0.5,
        "timeseries_metadata": {
            "title": f"{data['name']} Monthly Price ({data['unit']})",
            "description": (
                f"Monthly commodity price for {data['name']} in {data['unit']}. "
                f"Key raw material for EV batteries and energy storage supply chains. "
                f"Source: IMF Primary Commodity Price System."
            ),
            "keywords": data["keywords"],
        },
        "timeseries": data["timeseries"],
    }
    resp = api_post("/api/v1/forecasts", body)
    job_id = resp["job_id"]
    job_ids[code] = job_id
    print(f"   Job ID: {job_id}")

print()


# ── Step 4: Poll all jobs until complete ──────────────────────────────────────

print("⏳ Waiting for all forecasts to complete...")

results = {}   # code → final status response
pending = set(job_ids.keys())

while pending:
    for code in list(pending):
        job_id = job_ids[code]
        status_data = api_get(f"/api/v1/forecasts/{job_id}")
        status = status_data.get("status", "unknown")
        settled = status_data.get("settled", False)

        if settled:
            name = mineral_data[code]["name"]
            cost = status_data.get("eur_cents_final", 0)
            print(f"  ✅ {name}: {status}  (€{cost/100:.4f})")
            results[code] = status_data
            pending.remove(code)
        elif status == "failed":
            print(f"  ❌ {mineral_data[code]['name']}: FAILED")
            results[code] = status_data
            pending.remove(code)

    if pending:
        print(f"     Still running: {[mineral_data[c]['name'] for c in pending]} — checking again in 10s...", end="\r")
        time.sleep(10)

print()


# ── Step 5: Download artifacts for each mineral ───────────────────────────────

all_output = {}

for code, status_data in results.items():
    if status_data.get("status") != "completed":
        continue

    name = mineral_data[code]["name"]
    job_id = job_ids[code]
    print(f"📥 Downloading artifacts for {name}...")

    mineral_output = {"name": name, "job_id": job_id}

    # forecast.json
    try:
        fc = api_get_raw(f"/api/v1/forecasts/{job_id}/artifacts/forecast.json")
        mineral_output["forecast"] = fc
        series = fc.get("data", {}).get("forecast_series", {})
        print(f"   📈 Forecast ({mineral_data[code]['unit']}):")
        for date, vals in sorted(series.items()):
            pt = vals.get("forecast", "n/a")
            print(f"      {date}: {pt:,.2f}" if isinstance(pt, float) else f"      {date}: {pt}")
    except Exception as e:
        print(f"   ⚠️  Could not fetch forecast.json: {e}")

    # external_signals.json
    try:
        sig = api_get_raw(f"/api/v1/forecasts/{job_id}/artifacts/external_signals.json")
        mineral_output["external_signals"] = sig
        print(f"   🔍 External signals fetched")
    except Exception as e:
        print(f"   ⚠️  Could not fetch external_signals.json: {e}")

    all_output[code] = mineral_output
    print()


# ── Step 6: Standalone drivers for all minerals ───────────────────────────────

print("🔍 Running standalone Drivers requests for all minerals...")

for code, data in mineral_data.items():
    print(f"   {data['name']}...")
    try:
        body = {
            "timeseries_metadata": {
                "title": f"{data['name']} Price",
                "description": f"Monthly prices for {data['name']}, key EV mineral",
                "keywords": data["keywords"],
            },
            "timeseries": data["timeseries"],
        }
        drivers = api_post("/api/v1/drivers", body)
        if code in all_output:
            all_output[code]["drivers"] = drivers
        else:
            all_output[code] = {"name": data["name"], "drivers": drivers}
        print(f"   ✅ Done")
    except Exception as e:
        print(f"   ⚠️  Failed: {e}")

print()


# ── Step 7: Save everything ───────────────────────────────────────────────────

output_file = "ev_minerals_results.json"
with open(output_file, "w") as f:
    json.dump(all_output, f, indent=2)

print(f"💾 All results saved to {output_file}")
print()
print("🎉 Done! Summary:")
for code, out in all_output.items():
    sections = [k for k in ["forecast", "external_signals", "drivers"] if k in out]
    print(f"   • {out['name']}: {', '.join(sections)}")