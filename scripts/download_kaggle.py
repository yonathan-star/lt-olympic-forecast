"""
Downloads Olympic datasets from Kaggle.
Requires a Kaggle account and API token.

Setup (one time):
  1. Go to https://www.kaggle.com/settings → API → Create New Token
  2. Save the downloaded kaggle.json to:
       Windows: C:\\Users\\<you>\\.kaggle\\kaggle.json
  3. pip install kaggle

Datasets:
  - Olympedia historical 1896-2022
  - Paris 2024 full results
  - Tokyo 2020

Outputs:
  data/raw/kaggle/olympics_historical/
  data/raw/kaggle/paris_2024/
  data/raw/kaggle/tokyo_2020/
"""

import subprocess
import os
import sys

BASE_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "raw", "kaggle")

DATASETS = [
    {
        "slug": "josephcheng123456/olympic-historical-dataset-from-olympediaorg",
        "folder": "olympics_historical",
        "description": "Olympedia 1896–2022",
    },
    {
        "slug": "piterfm/paris-2024-olympic-summer-games",
        "folder": "paris_2024",
        "description": "Paris 2024 full results",
    },
    {
        "slug": "muhammadehsan02/olympic-summer-games-paris-2024",
        "folder": "tokyo_2020",
        "description": "Tokyo 2020 / Olympic summer games",
    },
]


def check_kaggle():
    try:
        result = subprocess.run(["kaggle", "--version"], capture_output=True, text=True)
        print(f"Kaggle CLI: {result.stdout.strip()}")
        return True
    except FileNotFoundError:
        print("ERROR: kaggle CLI not found.")
        print("Install it: pip install kaggle")
        return False


def download_dataset(slug: str, folder: str, description: str) -> None:
    out = os.path.join(BASE_DIR, folder)
    os.makedirs(out, exist_ok=True)
    print(f"\nDownloading {description}...")
    result = subprocess.run(
        ["kaggle", "datasets", "download", "-d", slug, "-p", out, "--unzip"],
        capture_output=True, text=True
    )
    if result.returncode == 0:
        files = os.listdir(out)
        print(f"  Done → {out}")
        print(f"  Files: {', '.join(files)}")
    else:
        print(f"  FAILED:\n{result.stderr}")
        print(f"  Manual download: https://www.kaggle.com/datasets/{slug}")


if __name__ == "__main__":
    if not check_kaggle():
        sys.exit(1)

    for ds in DATASETS:
        download_dataset(**ds)

    print("\nKaggle download complete.")
