# src/normalization/movielens.py

import sys
import polars as pl
from pathlib import Path

ROOT = Path().resolve()

while not (ROOT / "src").exists():
    ROOT = ROOT.parent

sys.path.append(str(ROOT / "src"))

from src.ingestion.sqlite import build_movielens_dataset


def normalize(df: pl.DataFrame) -> pl.DataFrame:
    return (
        df
        .select([
            "movieId",
            "title",
            "genres",
            "avg_rating",
            "num_ratings"
        ])
        .with_columns([
            # --- STRINGS CLEAN ---
            pl.col("title")
              .fill_null("")
              .str.strip_chars(),

            pl.col("genres")
              .fill_null("")
              .str.strip_chars(),

            # --- TYPES ---
            pl.col("movieId").cast(pl.Int32, strict=False),

            pl.col("avg_rating")
              .cast(pl.Float64, strict=False),

            pl.col("num_ratings")
              .cast(pl.Int32, strict=False),

            # --- SOURCE ---
            pl.lit("movielens").alias("source")
        ])
    )


def normalization_movielens() -> pl.DataFrame:
    raw = build_movielens_dataset()
    print("normalising ML...")
    return normalize(raw)


if __name__ == "__main__":
    df = normalization_movielens()
    print(df)
    print(df.schema)