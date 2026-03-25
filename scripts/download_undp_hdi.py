"""
Downloads the UNDP Human Development Index (HDI) dataset.
No credentials required.

Source: https://hdr.undp.org/data-center/documentation-and-downloads
Outputs:
  data/raw/undp/hdi.csv
"""

import urllib.request
import os

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "raw", "undp")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Direct CSV link from UNDP HDR data downloads (stable link, last verified 2024)
HDI_URL = "https://hdr.undp.org/sites/default/files/2023-24_HDR/HDR23-24_Statistical_Annex_HDI_Table.xlsx"

# The composite indices data table (CSV, all years 1990-present)
COMPOSITE_URL = "https://hdr.undp.org/sites/default/files/2023-24_HDR/HDR23-24_Statistical_Annex_HDI_Trends_Table.xlsx"


def download(url: str, filename: str) -> None:
    path = os.path.join(OUTPUT_DIR, filename)
    print(f"Downloading {filename}...")
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=60) as resp:
            data = resp.read()
        with open(path, "wb") as f:
            f.write(data)
        print(f"  Saved {len(data):,} bytes → {path}")
    except Exception as e:
        print(f"  FAILED: {e}")
        print(f"  Manual download: {url}")


if __name__ == "__main__":
    download(HDI_URL, "hdi_table.xlsx")
    download(COMPOSITE_URL, "hdi_trends.xlsx")

    print("\nIf downloads failed, get them manually at:")
    print("  https://hdr.undp.org/data-center/documentation-and-downloads")
    print("  → 'Human Development Index and components' tables")
    print("  Place the files in: data/raw/undp/")
