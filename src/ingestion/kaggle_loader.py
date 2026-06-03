import os
import zipfile
from pathlib import Path
import polars as pl
import subprocess

DATASET = "rounakbanik/the-movies-dataset"
DATA_DIR = Path("data/raw/kaggle")
CSV_FILE = DATA_DIR / "movies_metadata.csv"
ZIP_FILE = DATA_DIR / "the-movies-dataset.zip"


def download_kaggle_dataset():
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    if CSV_FILE.exists():
        print("Dataset already exists, skipping download.")
        return

    print("Downloading dataset from Kaggle...")

    subprocess.run([
        "kaggle", "datasets", "download",
        "-d", DATASET,
        "-p", str(DATA_DIR)
    ], check=True)

    with zipfile.ZipFile(ZIP_FILE, "r") as zip_ref:
        zip_ref.extractall(DATA_DIR)

    print("Download and extraction complete.")


def load_kaggle_movies() -> list[dict]:
    if not CSV_FILE.exists():
        download_kaggle_dataset()

    print("Loading Kaggle Movies dataset...")

    df = pl.read_csv(CSV_FILE, ignore_errors=True)

    df = df.select([
        "title",
        "overview",
        "tagline",
        "genres",
        "release_date",
        "vote_average",
        "popularity"
    ])


    # → list[dict]
    # records = df.to_dicts()
    # print(f"Loaded {len(records)} records")
    print(f"Loaded {len(df)} records")

    return df


if __name__ == "__main__":
    print("start")
    data = load_kaggle_movies()
    print(data[0])