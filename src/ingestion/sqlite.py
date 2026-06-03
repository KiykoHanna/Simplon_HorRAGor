import sqlite3
import pandas as pd
import polars as pl
import requests
import zipfile
from pathlib import Path

URL = "https://files.grouplens.org/datasets/movielens/ml-1m.zip"
DATA_DIR= "data/raw/movielens"
DB_PATH = "movielens.db"

def download_movielens_1m(output_dir="data/raw/movielens"):
    print("start")
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    zip_path = output_path / "ml-1m.zip"

    # if exist
    if zip_path.exists():
        print("MovieLens 1M already downloaded")
    else:
        print("Downloading MovieLens 1M...")
        response = requests.get(URL)
        response.raise_for_status()

        with open(zip_path, "wb") as f:
            f.write(response.content)

        print("Download completed")

    # unzip
    extract_path = output_path / "ml-1m"

    if extract_path.exists():
        print("Already extracted")
    else:
        print("Extracting...")
        with zipfile.ZipFile(zip_path, "r") as z:
            z.extractall(output_path)

        print("Extraction completed")

    movies = pd.read_csv(
        extract_path / "movies.dat",
        sep="::",
        engine="python",
        names=["movieId", "title", "genres"],
        encoding="latin-1"
    )

    ratings = pd.read_csv(
        extract_path / "ratings.dat",
        sep="::",
        engine="python",
        names=["userId", "movieId", "rating", "timestamp"],
        encoding="latin-1"
    )

    return movies, ratings


def load_movies(conn):
    query = """
    SELECT 
        movieId,
        title,
        genres
    FROM movies
    """
    return pd.read_sql(query, conn)

def load_ratings(conn):
    query = """
    SELECT 
        movieId,
        AVG(rating) as avg_rating,
        COUNT(rating) as num_ratings
    FROM ratings
    GROUP BY movieId
    HAVING COUNT(rating) >= 100
    """
    return pd.read_sql(query, conn)

def build_movielens_dataset():
    conn = creating_db()

    movies = load_movies(conn)
    ratings = load_ratings(conn)

    df = movies \
        .merge(ratings, on="movieId", how="left") 

    return pl.from_pandas(df)

def creating_db():
    conn = sqlite3.connect(DB_PATH)

    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='movies'")
    exists = cursor.fetchone()

    if exists:
        print("DB already exists")
        return conn

    movies, ratings = download_movielens_1m(DATA_DIR)

    movies.to_sql("movies", conn, index=False)
    ratings.to_sql("ratings", conn, index=False)

    print("DB created")

    return conn


if __name__ == "__main__":

    df = build_movielens_dataset()
    print(df.head())