# src/cleaning/movie_cleaner.py

from pathlib import Path
import polars as pl

from src.normalization.n_tmdb import normalization_tmdb
from src.normalization.n_imdb import normalization_imdb
from src.normalization.n_kaggle import normalization_kaggle
from src.normalization.n_movielens import normalization_movielens

ROOT = Path(__file__).resolve().parents[2]

PROCESSED_DIR = ROOT / "data" / "processed"
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)


def clean_movies(df: pl.DataFrame) -> pl.DataFrame:

    return (
        df
        .unique()
        .filter(pl.col("title").is_not_null())
        .filter(pl.col("title").str.len_chars() > 0)
        .with_columns(
            pl.col("title")
            .str.to_lowercase()
            .str.strip_chars()
            .str.replace_all(r"\s+", " ")
            .alias("title_clean")
        )
    )


def clean_imdb(df: pl.DataFrame) -> pl.DataFrame:

    return (
        clean_movies(df)
        .filter(pl.col("year") > 1900)
        .filter(
            pl.col("genres")
            .fill_null("")
            .str.contains("Horror")
        )
        .unique(subset=["imdb_id"])
    )


def clean_tmdb(df: pl.DataFrame) -> pl.DataFrame:

    return (
        clean_movies(df)
        .filter(pl.col("tmdb_id").is_not_null())
        .unique(subset=["tmdb_id"])
    )


def clean_movielens(df: pl.DataFrame) -> pl.DataFrame:

    return (
        clean_movies(df)
        .filter(pl.col("num_ratings") >= 100)
        .unique(subset=["movieId"])
    )


def clean_kaggle(df: pl.DataFrame) -> pl.DataFrame:

    return (
        clean_movies(df)
        .unique(subset=["title", "year"])
    )


def save_cleaned_dataset(
    df: pl.DataFrame,
    source_name: str
) -> Path:

    parquet_file = PROCESSED_DIR / f"{source_name}.parquet"

    df.write_parquet(parquet_file)

    try:
        csv_file = PROCESSED_DIR / f"{source_name}.csv"

        csv_df = df

        for col_name, dtype in df.schema.items():
            if isinstance(dtype, pl.List):
                csv_df = csv_df.with_columns(
                    pl.col(col_name)
                    .cast(pl.List(pl.Utf8))
                    .list.join(", ")
                    .alias(col_name)
                )

        if "cast" in df.columns:
            csv_df = df.with_columns(
                pl.col("cast")
                .cast(pl.List(pl.Utf8))
                .list.join(", ")
            )

        csv_df.write_csv(csv_file)

    except Exception as e:
        print(f"CSV export skipped for {source_name}: {e}")

    print(f"Saved: {parquet_file}")

    return parquet_file


def process_all_sources():

    datasets = [
        ("tmdb_clean", lambda: clean_tmdb(normalization_tmdb())),
        ("imdb_clean", lambda: clean_imdb(normalization_imdb())),
        # ("rotten_tomatoes_clean", lambda: clean_movielens(normalization_rotten_tomatoes())),
        ("movielens_clean", lambda: clean_movielens(normalization_movielens())),
        ("kaggle_clean", lambda: clean_kaggle(normalization_kaggle()))
    ]

    for name, loader in datasets:

        parquet_file = PROCESSED_DIR / f"{name}.parquet"

        if parquet_file.exists():
            print(f"Skipping {name}: already exists")
            continue

        print(f"Processing {name}...")

        try:
            df = loader()

            print(f"Rows: {len(df)}")

            save_cleaned_dataset(df, name)

        except Exception as e:
            print(f"Error processing {name}: {e}")

    print("All datasets processed.")


if __name__ == "__main__":
    process_all_sources()