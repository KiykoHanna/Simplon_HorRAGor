# main.py

from pathlib import Path

from src.cleaning.movie_cleaner import process_all_sources
from src.matching.build_gold_dataset import build_gold_dataset_pipeline

# ingestion
from src.ingestion.tmdb import extract_tmdb_raw
from src.ingestion.imdb import extract_imdb
from src.ingestion.kaggle_movies import load_kaggle_movies
from src.ingestion.movielens import build_movielens_dataset


ROOT = Path(__file__).resolve().parent

RAW_DIR = ROOT / "data" / "raw"
PROCESSED_DIR = ROOT / "data" / "processed"
GOLD_DIR = ROOT / "data" / "gold"


def processed_exists() -> bool:

    required = [
        "tmdb_clean.parquet",
        "imdb_clean.parquet",
        "kaggle_clean.parquet",
        "movielens_clean.parquet",
    ]

    return all(
        (PROCESSED_DIR / file).exists()
        for file in required
    )


def gold_exists() -> bool:

    return (
        GOLD_DIR / "gold_movies.parquet"
    ).exists()


def run_ingestion():

    print("\n=== INGESTION ===")

    try:
        print("TMDB...")
        extract_tmdb_raw()
    except Exception as e:
        print(f"TMDB error: {e}")

    try:
        print("IMDb...")
        extract_imdb(limit=1000)
    except Exception as e:
        print(f"IMDb error: {e}")

    try:
        print("Kaggle...")
        load_kaggle_movies()
    except Exception as e:
        print(f"Kaggle error: {e}")

    try:
        print("MovieLens...")
        build_movielens_dataset()
    except Exception as e:
        print(f"MovieLens error: {e}")


def run_cleaning():

    print("\n=== CLEANING ===")
    process_all_sources()


def run_gold():

    print("\n=== GOLD DATASET ===")
    build_gold_dataset_pipeline()


def main():

    print("\nHorRAGor ETL Pipeline\n")

    if not processed_exists():

        print(
            "Processed datasets not found."
        )

        run_ingestion()
        run_cleaning()

    else:

        print(
            "Processed datasets already exist."
        )

    if not gold_exists():

        print(
            "Gold dataset not found."
        )

        run_gold()

    else:

        print(
            "Gold dataset already exists."
        )

    print("\nPipeline completed.")


if __name__ == "__main__":
    main()