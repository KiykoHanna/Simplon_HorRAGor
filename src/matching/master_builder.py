# src/matching/master_builder.py

import polars as pl
from rapidfuzz import process, fuzz


def add_key(df: pl.DataFrame) -> pl.DataFrame:
    return df.with_columns(
        pl.col("title")
        .fill_null("")
        .str.to_lowercase()
        .str.replace_all(r"\s+", " ")
        .str.strip_chars()
        .alias("title_key")
    )


def fuzzy_match_title(
    title: str,
    candidates: list[str],
    threshold: int = 90
):

    if not title:
        return None

    result = process.extractOne(
        title,
        candidates,
        scorer=fuzz.WRatio
    )

    if result and result[1] >= threshold:
        return result[0]

    return None


def fuzzy_enrich(
    master: pl.DataFrame,
    source: pl.DataFrame,
    source_name: str,
    threshold: int = 90
) -> pl.DataFrame:

    source_titles = source["title_key"].to_list()

    matches = []

    for row in master.iter_rows(named=True):

        match = fuzzy_match_title(
            row["title_key"],
            source_titles,
            threshold
        )

        matches.append(match)

    master = master.with_columns(
        pl.Series(f"fuzzy_{source_name}", matches)
    )

    return master


def build_master_table(
    tmdb: pl.DataFrame,
    imdb: pl.DataFrame,
    kaggle: pl.DataFrame,
    movielens: pl.DataFrame
) -> pl.DataFrame:

    # KEYS ---------------------------

    tmdb = add_key(tmdb)
    imdb = add_key(imdb)
    kaggle = add_key(kaggle)
    movielens = add_key(movielens)

    # EXACT MATCH ---------------------------

    master = tmdb.join(
        imdb,
        on=["title_key", "year"],
        how="left",
        suffix="_imdb"
    )

    master = master.join(
        kaggle,
        on=["title_key", "year"],
        how="left",
        suffix="_kaggle"
    )

    master = master.join(
        movielens,
        on="title_key",
        how="left",
        suffix="_ml"
    )

    # FUZZY FALLBACK INFO ---------------------------

    master = fuzzy_enrich(
        master,
        imdb,
        "imdb"
    )

    master = fuzzy_enrich(
        master,
        kaggle,
        "kaggle"
    )

    master = fuzzy_enrich(
        master,
        movielens,
        "movielens"
    )

    # MASTER ID ---------------------------
    master = master.with_row_index("master_id")

    # DEDUP ---------------------------
    master = master.unique( subset=["title_key", "year"])
    return master