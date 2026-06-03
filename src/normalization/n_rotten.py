# src/normalization/rotten_tomatoes.py

import sys
import polars as pl
from pathlib import Path

ROOT = Path().resolve()

while not (ROOT / "src").exists():
    ROOT = ROOT.parent

sys.path.append(str(ROOT / "src"))

from src.ingestion.rotten_scraper import extract_rotten_tomatoes


def normalize(df: pl.DataFrame) -> pl.DataFrame:
    return (
        df
        .select([
            "title",
            "tomatometer_score",
            "audience_score",
            "critics_consensus",
            "url"
        ])
        .with_columns([
            # --- STRINGS CLEAN ---
            pl.col("title")
              .fill_null("")
              .str.strip_chars(),

            pl.col("critics_consensus")
              .fill_null("")
              .str.strip_chars(),

            pl.col("url")
              .fill_null("")
              .str.strip_chars(),

            # --- TYPES ---
            pl.col("tomatometer_score")
              .cast(pl.Int32, strict=False),

            pl.col("audience_score")
              .cast(pl.Int32, strict=False),

            # --- SOURCE ---
            pl.lit("rotten_tomatoes").alias("source")
        ])
    )


def normalization_rotten_tomatoes(movies: list[str]) -> pl.DataFrame:
    raw = extract_rotten_tomatoes(movies)
    print("normalising RT...")
    return normalize(raw)


if __name__ == "__main__":
    test_movies = ["The Shining", "It", "The Conjuring"]
    df = normalization_rotten_tomatoes(test_movies)
    print(df)
    print(df.schema)