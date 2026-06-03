import sys
import polars as pl
from pathlib import Path

ROOT = Path().resolve()

# поднимаемся до проекта (а не src!)
while not (ROOT / "src").exists():
    ROOT = ROOT.parent

sys.path.append(str(ROOT / "src"))

from src.ingestion.tmdb import extract_tmdb_raw

def normalize(df: pl.DataFrame) -> pl.DataFrame:
    return (
        df
        .select([
            "tmdb_id",
            "title",
            "original_title",
            "overview",
            "release_date",
            "vote_average",
            "vote_count",
            "popularity",
            "original_language",
            "adult",
            "poster_path",
            "backdrop_path",
            "genre_ids",
            "source"
        ])
        .with_columns([
            # --- CLEAN STRINGS ---
            pl.col("title").fill_null("").str.strip_chars(),
            pl.col("original_title").fill_null("").str.strip_chars(),
            pl.col("overview").fill_null("").str.strip_chars(),

            # --- SAFE YEAR EXTRACTION ---
            pl.col("release_date")
              .cast(pl.Utf8, strict=False)
              .str.slice(0, 4)
              .cast(pl.Int32, strict=False)
              .alias("year"),


            # --- TYPE NORMALIZATION ---
            pl.col("vote_average").cast(pl.Float64, strict=False),
            pl.col("vote_count").cast(pl.Int32, strict=False),
            pl.col("popularity").cast(pl.Float64, strict=False),

            # --- BOOLEAN SAFETY ---
            pl.col("adult").cast(pl.Boolean, strict=False),
        ])
    )


def normalization_tmdb() -> pl.DataFrame:
    print("normalising TMDB...")
    return normalize(extract_tmdb_raw())
