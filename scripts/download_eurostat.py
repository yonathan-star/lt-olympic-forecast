"""
Downloads Eurostat government expenditure data (COFOG).
Focuses on recreation, culture and religion (GF08) as a share of GDP.
No credentials required — uses the Eurostat JSON API.

Source: https://ec.europa.eu/eurostat/databrowser/view/gov_10a_exp
Outputs:
  data/raw/eurostat/gov_expenditure_cofog.csv
"""

import urllib.request
import json
import csv
import os

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "raw", "eurostat")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Eurostat REST API — government expenditure by function (% of GDP)
# Dataset: gov_10a_exp | unit=PC_GDP | cofog99=GF08 (Recreation, culture & religion)
API_URL = (
    "https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/gov_10a_exp"
    "?format=JSON"
    "&lang=EN"
    "&unit=PC_GDP"
    "&cofog99=GF08"        # Recreation, culture and religion
    "&na_item=TE"          # Total expenditure
    "&sector=S13"          # General government
)


def fetch_eurostat(url: str) -> tuple[list[str], list[dict]]:
    print("Fetching Eurostat COFOG data...")
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=60) as resp:
        data = json.loads(resp.read())

    dims = data["dimension"]
    geo_labels = dims["geo"]["category"]["label"]
    time_labels = dims["time"]["category"]["label"]

    geo_ids = list(dims["geo"]["category"]["index"].keys())
    time_ids = list(dims["time"]["category"]["index"].keys())

    values = data["value"]
    n_time = len(time_ids)

    rows = []
    for g_i, geo in enumerate(geo_ids):
        for t_i, time in enumerate(time_ids):
            flat_idx = str(g_i * n_time + t_i)
            value = values.get(flat_idx)
            rows.append({
                "country_code": geo,
                "country_name": geo_labels.get(geo, geo),
                "year": time,
                "recreation_pct_gdp": value,
            })

    return rows


def save(rows: list[dict], filename: str) -> None:
    path = os.path.join(OUTPUT_DIR, filename)
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["country_code", "country_name", "year", "recreation_pct_gdp"])
        writer.writeheader()
        writer.writerows(rows)
    non_null = sum(1 for r in rows if r["recreation_pct_gdp"] is not None)
    print(f"Saved {len(rows):,} rows ({non_null:,} with values) → {path}")


if __name__ == "__main__":
    rows = fetch_eurostat(API_URL)
    save(rows, "gov_expenditure_cofog_gf08.csv")
    print("Eurostat download complete.")
    print("\nNote: GF08 = Recreation, culture & religion (% of GDP).")
    print("To get total sport-specific data, use the Eurostat browser manually:")
    print("  https://ec.europa.eu/eurostat/databrowser/view/gov_10a_exp")
