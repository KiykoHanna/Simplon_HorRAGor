import polars as pl
from database.connection import get_client

def load_gold_to_supabase():
    client = get_client()

    df = pl.read_parquet("data/gold/gold_movies.parquet")
    df = df.group_by(df.columns).first()
    df = df.select([
        "master_id",
        "tmdb_id",
        "imdb_id",
        "movieId",

        "title",
        "original_title",
        "overview",
        "tagline",

        "release_date",
        "year",

        "genres",
        "genre_ids",
        "cast",

        "vote_average",
        "vote_count",
        "popularity",

        "avg_rating",
        "num_ratings",

        "tomatometer_score",
        "audience_score",
        "critics_consensus",

        "original_language",
        "adult",

        "poster_path",
        "backdrop_path",
        "url"
    ])

    # clean 
    # text columns
    df = df.with_columns([
        pl.col("genre_ids").cast(pl.List(pl.Utf8)).list.join(", ").alias("genre_ids"),
        pl.col("cast").list.join(", ").alias("actor")
    ])

    text_cols = [
        "title", "overview", "tagline",
        "genres", "actor", "poster_path", "backdrop_path"
    ]

    df = df.with_columns([ *[pl.col(c).fill_null("") for c in text_cols]])

    df = df.rename({"movieId": "movieid"})
    df = df.drop("cast")

    records = df.to_dicts()

    BATCH_SIZE = 300

    for i in range(0, len(records), BATCH_SIZE):
        batch = records[i:i+BATCH_SIZE]

        try:
            res = client.table("movies_gold").upsert(batch).execute()
            print(f"OK {i}-{i+BATCH_SIZE}")

        except Exception as e:
            print(f"ERROR {i}: {e}")