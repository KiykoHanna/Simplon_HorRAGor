# src/normalization/kaggle.py

import sys
import polars as pl
from pathlib import Path

ROOT = Path().resolve()

while not (ROOT / "src").exists():
    ROOT = ROOT.parent

sys.path.append(str(ROOT / "src"))

from src.ingestion.kaggle_loader import load_kaggle_movies


def normalize(df: pl.DataFrame) -> pl.DataFrame:
    return (
        df
        .select([
            "title",
            "overview",
            "tagline",
            "genres",
            "release_date",
            "vote_average",
            "popularity"
        ])
        .with_columns([
            # --- STRINGS CLEAN ---
            pl.col("title")
              .fill_null("")
              .str.strip_chars(),

            pl.col("overview")
              .fill_null("")
              .str.strip_chars(),

            pl.col("tagline")
              .fill_null("")
              .str.strip_chars(),

            pl.col("genres")
              .fill_null("")
              .str.strip_chars(),

            # --- YEAR EXTRACTION ---
            pl.col("release_date")
              .cast(pl.Utf8, strict=False)
              .str.slice(0, 4)
              .cast(pl.Int32, strict=False)
              .alias("year"),

            # --- TYPES ---
            pl.col("vote_average")
              .cast(pl.Float64, strict=False),

            pl.col("popularity")
              .cast(pl.Float64, strict=False),

            # --- SOURCE ---
            pl.lit("kaggle").alias("source")
        ])
    )


def normalization_kaggle() -> pl.DataFrame:
    raw = load_kaggle_movies()
    print("normalising Kaggle...")
    return normalize(raw)


if __name__ == "__main__":
    df = normalization_kaggle()
    print(df)
    print(df.schema)