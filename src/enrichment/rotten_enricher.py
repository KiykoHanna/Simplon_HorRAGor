# src/enrichment/rotten_enricher.py

import polars as pl
import sys
from pathlib import Path

ROOT = Path().resolve()

while not (ROOT / "src").exists():
    ROOT = ROOT.parent

sys.path.append(str(ROOT / "src"))

from src.ingestion.rotten_scraper import extract_rotten_tomatoes


def enrich_with_rotten(gold_df: pl.DataFrame) -> pl.DataFrame:

    # 1. берём список фильмов из gold
    titles = (
        gold_df
        .select("title")
        .unique()
        .to_series()
        .to_list()
    )

    # 2. вызываем scraper
    rotten_df = extract_rotten_tomatoes(titles)

    # 3. нормализуем ключ
    rotten_df = rotten_df.with_columns(
        pl.col("title")
        .fill_null("")
        .str.to_lowercase()
        .str.replace_all(r"\s+", " ")
        .str.strip_chars()
        .alias("title_key")
    )

    gold_df = gold_df.with_columns(
        pl.col("title")
        .fill_null("")
        .str.to_lowercase()
        .str.replace_all(r"\s+", " ")
        .str.strip_chars()
        .alias("title_key")
    )

    # 4. join
    return gold_df.join(
        rotten_df,
        on="title_key",
        how="left"
    )