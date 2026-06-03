from pyspark.sql import SparkSession
from pathlib import Path
from pyspark.sql.functions import col, explode, split, regexp_replace

DATA_DIR = Path("data/raw/kaggle")

MD_FILE = DATA_DIR / "movies_metadata.csv"
KW_FILE = DATA_DIR / "keywords.csv"
L_FILE = DATA_DIR / "links.csv"

spark = SparkSession.builder \
    .appName("KaggleMovieIngestion") \
    .getOrCreate()


def load_movies_metadata(path: str):
    df = spark.read.csv(
        path,
        header=True,
        inferSchema=True,
        multiLine=True,
        escape='"'
    )

    df_clean = (
        df.select(
            col("id").alias("kaggle_id"),
            col("title"),
            col("overview"),
            col("release_date"),
            col("vote_average"),
            col("vote_count"),
            col("popularity"),
            col("genres")
        )
        .dropna(subset=["kaggle_id", "title"])
        .filter(col("title") != "")
    )

    return df_clean

def load_keywords(path: str):
    df = spark.read.csv(
        path,
        header=True,
        inferSchema=True,
        multiLine=True,
        escape='"'
    )
    print(f"loaded {df.count()}")
    # keywords обычно JSON-like string → чистим
    df_clean = (
        df.select(
            col("id").alias("kaggle_id"),
            col("keywords")
        )
        .withColumn(
            "keywords_clean",
            regexp_replace(col("keywords"), "[\\[\\]{}\"']", "")
        )
    )
    print(f"cleaned {df_clean.count()}")
    return df_clean

def load_links(path: str):
    df = spark.read.csv(
        path,
        header=True,
        inferSchema=True
    )
    print(f"loaded links {df.count()}")
    df_clean = (
        df.select(
            col("movieId").alias("kaggle_id"),
            col("imdbId").alias("imdb_id"),
            col("tmdbId").alias("tmdb_id")
        )
        .dropna(subset=["kaggle_id"])
    )
    print(f"cleaned links {df_clean.count()}")
    return df_clean

def extract_kaggle(movies_path, keywords_path, links_path):

    movies = load_movies_metadata(movies_path)
    keywords = load_keywords(keywords_path)
    links = load_links(links_path)

    df = movies \
        .join(keywords, "kaggle_id", "left") \
        .join(links, "kaggle_id", "left")

    return df

if __name__ == "__main__":

    df = extract_kaggle(
        str(MD_FILE),
        str(KW_FILE),
        str(L_FILE)
    )

    df.show(5)