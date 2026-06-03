# src/matching/build_gold_dataset.py

from pathlib import Path
import polars as pl

from src.enrichment.rotten_enricher import enrich_with_rotten
from src.matching.master_builder import build_master_table

ROOT = Path(__file__).resolve().parents[2]

PROCESSED_DIR = ROOT / "data" / "processed"
GOLD_DIR = ROOT / "data" / "gold"

GOLD_DIR.mkdir(parents=True, exist_ok=True)


def load_processed(name: str) -> pl.DataFrame:

    path = PROCESSED_DIR / f"{name}.parquet"

    if not path.exists():
        raise FileNotFoundError(
            f"Processed file not found: {path}"
        )

    print(f"Loading {path.name}")

    return pl.read_parquet(path)


def save_gold(df: pl.DataFrame):

    parquet_file = GOLD_DIR / "gold_movies.parquet"
    csv_file = GOLD_DIR / "gold_movies.csv"

    df.write_parquet(parquet_file)

    try:

        csv_df = df

        for col_name, dtype in df.schema.items():

            if isinstance(dtype, pl.List):

                csv_df = csv_df.with_columns(
                    pl.col(col_name)
                    .map_elements(
                        lambda x: ", ".join(map(str, x))
                        if x is not None else "",
                        return_dtype=pl.Utf8
                    )
                    .alias(col_name)
                )

        csv_df.write_csv(csv_file)

    except Exception as e:

        print(
            f"CSV export skipped: {e}"
        )

    print(f"Saved: {parquet_file}")
    print(f"Saved: {csv_file}")


def build_gold_dataset_pipeline():

    print("Loading processed datasets...")

    tmdb = load_processed("tmdb_clean")
    imdb = load_processed("imdb_clean")
    kaggle = load_processed("kaggle_clean")
    movielens = load_processed("movielens_clean")

    print("Building master table...")

    gold = build_master_table(
        tmdb=tmdb,
        imdb=imdb,
        kaggle=kaggle,
        movielens=movielens
    )

    print("Enriching with Rotten Tomatoes...")

    gold = enrich_with_rotten(gold)

    print("Saving gold dataset...")

    save_gold(gold)

    return gold


if __name__ == "__main__":

    df = build_gold_dataset_pipeline()

    print()
    print("Gold dataset created")
    print(df.head())