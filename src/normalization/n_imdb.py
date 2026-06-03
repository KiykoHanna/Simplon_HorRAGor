# src/normalization/imdb.py

import sys
import polars as pl
from pathlib import Path

ROOT = Path().resolve()

while not (ROOT / "src").exists():
    ROOT = ROOT.parent

sys.path.append(str(ROOT / "src"))

from src.ingestion.imdb import extract_imdb


def normalize(df: pl.DataFrame) -> pl.DataFrame:
    return (
        df
        .select([
            "imdb_id",
            "title",
            "year",
            "genres",
            "cast"
        ])
        .with_columns([
            # --- CLEAN STRINGS ---
            pl.col("imdb_id").cast(pl.Utf8),

            pl.col("title")
              .fill_null("")
              .str.strip_chars(),

            pl.col("genres")
              .fill_null("")
              .str.strip_chars(),

            # --- YEAR ---
            pl.col("year")
              .cast(pl.Int32, strict=False),

            # --- SOURCE ---
            pl.lit("imdb").alias("source")
        ])
    )


def normalization_imdb(limit: int = 1000) -> pl.DataFrame:
    return normalize(extract_imdb(limit=limit))


if __name__ == "__main__":
    df = normalization_imdb(5)
    print(df)
    print(df.schema)