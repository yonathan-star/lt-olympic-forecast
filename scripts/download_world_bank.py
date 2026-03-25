"""
Downloads World Bank indicators via their public API.
No credentials required.

Outputs:
  data/raw/world_bank/gdp_per_capita.csv
  data/raw/world_bank/population.csv
  data/raw/world_bank/gni_per_capita.csv
"""

import urllib.request
import json
import csv
import os

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "raw", "world_bank")
os.makedirs(OUTPUT_DIR, exist_ok=True)

INDICATORS = {
    "gdp_per_capita": "NY.GDP.PCAP.CD",
    "population":     "SP.POP.TOTL",
    "gni_per_capita": "NY.GNP.PCAP.CD",
}

BASE_URL = "https://api.worldbank.org/v2/country/all/indicator/{indicator}?format=json&per_page=5000&mrv=65"


def fetch_indicator(indicator_code: str) -> list[dict]:
    url = BASE_URL.format(indicator=indicator_code)
    records = []
    page = 1
    while True:
        paged = url + f"&page={page}"
        with urllib.request.urlopen(paged, timeout=30) as resp:
            data = json.loads(resp.read())
        meta, rows = data[0], data[1]
        if rows:
            records.extend(rows)
        if page >= meta["pages"]:
            break
        page += 1
    return records


def save(records: list[dict], name: str) -> None:
    path = os.path.join(OUTPUT_DIR, f"{name}.csv")
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["country_iso3", "country_name", "year", "value"])
        for r in records:
            writer.writerow([
                r["countryiso3code"],
                r["country"]["value"],
                r["date"],
                r["value"],
            ])
    print(f"Saved {len(records):,} rows -> {path}")


if __name__ == "__main__":
    for name, code in INDICATORS.items():
        print(f"Fetching {name} ({code})...")
        rows = fetch_indicator(code)
        save(rows, name)
    print("World Bank download complete.")
