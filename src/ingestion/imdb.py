import polars as pl
from pathlib import Path
import requests
import gzip
import shutil
from tqdm import tqdm

ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT / "data/raw/imdb"

IMDB_URLS = {
    "basics": "https://datasets.imdbws.com/title.basics.tsv.gz",
    "principals": "https://datasets.imdbws.com/title.principals.tsv.gz",
    "names": "https://datasets.imdbws.com/name.basics.tsv.gz",
}

TITLE_FILE = DATA_DIR / "basics.tsv"
PRINCIPALS_FILE = DATA_DIR / "principals.tsv"
NAME_FILE = DATA_DIR / "names.tsv"


def download_file(url: str, output_path: Path):
    response = requests.get(url, stream=True)
    response.raise_for_status()

    total_size = int(response.headers.get("content-length", 0))

    with open(output_path, "wb") as f, tqdm(
        desc=output_path.name,
        total=total_size,
        unit="B",
        unit_scale=True
    ) as pbar:

        for chunk in response.iter_content(chunk_size=1024 * 1024):
            if chunk:
                f.write(chunk)
                pbar.update(len(chunk))


def download_imdb_tsv():
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    for name, url in IMDB_URLS.items():
        gz_path = DATA_DIR / f"{name}.tsv.gz"

        if gz_path.exists():
            print(f"{name} already downloaded")
            continue

        print(f"Downloading {name}...")
        download_file(url, gz_path)

    print("IMDb download completed.")

def unzip_gz(file_path: Path):
    output_path = file_path.with_suffix("")  # remove .gz

    if output_path.exists():
        return

    with gzip.open(file_path, "rb") as f_in:
        with open(output_path, "wb") as f_out:
            shutil.copyfileobj(f_in, f_out)


def unzip_all():
    folder = DATA_DIR

    for file in folder.glob("*.gz"):
        print(f"Unzipping {file.name}")
        unzip_gz(file)


def load_imdb_basics():
    rows = []
    path = TITLE_FILE

    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        header = f.readline().strip().split("\t")

        # индексы колонок (важно для скорости)
        idx_tconst = header.index("tconst")
        idx_title = header.index("primaryTitle")
        idx_year = header.index("startYear")
        idx_genres = header.index("genres")
        idx_type = header.index("titleType")

        for line in f:
            parts = line.rstrip("\n").split("\t")

            if len(parts) != len(header):
                continue

            # --- ФИЛЬТРЫ ---
            if parts[idx_type] != "movie":
                continue

            genres = parts[idx_genres]
            if genres == "\\N" or "Horror" not in genres:
                continue

            year = parts[idx_year]
            if year == "\\N":
                continue

            rows.append([
                parts[idx_tconst],
                parts[idx_title],
                year,
                genres
            ])

    return pl.DataFrame(
        rows,
        schema=["tconst", "primaryTitle", "startYear", "genres"],
        orient="row"
    )


def load_imdb_cast():
    principals_rows = []
    names_rows = {}

    # ---- names ----
    with open(NAME_FILE, "r", encoding="utf-8", errors="ignore") as f:
        header = f.readline().strip().split("\t")

        for line in f:
            parts = line.rstrip("\n").split("\t")
            if len(parts) != len(header):
                continue

            names_rows[parts[0]] = parts[1]  # nconst -> primaryName

    # ---- principals ----
    with open(PRINCIPALS_FILE, "r", encoding="utf-8", errors="ignore") as f:
        header = f.readline().strip().split("\t")

        for line in f:
            parts = line.rstrip("\n").split("\t")

            if len(parts) != len(header):
                continue

            # category filter
            if parts[3] not in ("actor", "actress"):
                continue

            principals_rows.append({
                "tconst": parts[0],
                "nconst": parts[2]
            })

    # ---- convert to polars ----
    df = pl.DataFrame(principals_rows)

    df = df.with_columns(
        pl.col("nconst").replace(names_rows).alias("primaryName")
    )

    return df.select([
        "tconst",
        "primaryName"
    ])


def extract_imdb(limit=1000):
    print("extract IMDB...")
    download_imdb_tsv()
    unzip_all()


    basics = load_imdb_basics()
    cast = load_imdb_cast()

    movies = basics.head(limit)

    result = []

    for row in movies.iter_rows(named=True):
        tconst = row["tconst"]

        movie_cast = (
            cast.filter(pl.col("tconst") == tconst)
            .select("primaryName")
            .to_series()
            .to_list()
        )

        result.append({
            "imdb_id": tconst,
            "title": row["primaryTitle"],
            "year": row["startYear"],
            "genres": row["genres"],
            "cast": movie_cast[:5]
        })

    return pl.DataFrame(result)


if __name__ == "__main__":

    data = extract_imdb(5)

    print(data[:2])