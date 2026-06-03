from pathlib import Path



from src.clearning.movie_clean import process_all_sources
from src.merging.build_gold_dataset import build_gold_dataset_pipeline

from database.load_gold import load_gold_to_supabase  

ROOT = Path(__file__).resolve().parents[1]   

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

    return all((PROCESSED_DIR / f).exists() for f in required)


def gold_exists() -> bool:
    return (GOLD_DIR / "gold_movies.parquet").exists()


def run_cleaning():
    print("\n=== CLEANING ===")
    process_all_sources()


def run_gold():
    print("\n=== GOLD DATASET BUILD ===")
    build_gold_dataset_pipeline()


def run_supabase_load():
    print("\n=== SUPABASE LOAD ===")
    load_gold_to_supabase()  

def main():
    print("\nHorRAGor ETL Pipeline\n")
    print("FILE:", __file__)
    print("ROOT:", ROOT)
    print("PROCESSED_DIR:", PROCESSED_DIR)
    print("EXISTS:", PROCESSED_DIR.exists())
    # 1. INGESTION + CLEANING
    if not processed_exists():
        print("Processed datasets not found.")
        run_cleaning()
    else:
        print("Processed datasets already exist.")

    # 2. GOLD BUILD
    if not gold_exists():
        print("Gold dataset not found.")
        run_gold()
    else:
        print("Gold dataset already exists.")

    # 3. SUPABASE LOAD (НОВЫЙ ЭТАП)
    run_supabase_load()

    print("\nPipeline completed.")


if __name__ == "__main__":
    main()