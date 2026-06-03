# src/database/load_gold.py

import polars as pl

from connection import get_engine

GOLD_FILE = "data/gold/gold_movies.parquet"

df = pl.read_parquet(GOLD_FILE)

# Polars -> Pandas
pdf = df.to_pandas()

pdf.to_sql(
    "movies",
    get_engine(),
    if_exists="replace",
    index=False
)

print("Movies loaded")