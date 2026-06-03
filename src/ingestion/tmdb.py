import requests
from dotenv import load_dotenv
import polars as pl
import time
import os

load_dotenv()

TMDB_API_KEY = os.getenv("TMDB_API_KEY")
TMDB_URL = os.getenv("TMDB_URL")
MAX_PAGES = 500

def discover_horror_pages():
    """stream pages only"""
    page = 1

    while page <= MAX_PAGES:
        params = {
            "api_key": TMDB_API_KEY,
            "with_genres": 27,  # horror
            "sort_by": "popularity.desc",
            "page": page
        }

        r = requests.get(f"{TMDB_URL}/discover/movie", params=params)
        r.raise_for_status()
        data = r.json()

        yield data["results"]

        if page >= data.get("total_pages", 1):
            break

        page += 1
        time.sleep(0.25)

def extract_tmdb_raw():
    print("extract TMDB...")
    rows = []

    for page in discover_horror_pages():
        for m in page:

            rows.append({
                # IDs (ключи для MDM)
                "tmdb_id": m.get("id"),
                "imdb_id": None,  # можно позже заполнить через /movie/{id}/external_ids

                # основные поля
                "title": m.get("title"),
                "original_title": m.get("original_title"),

                # текстовый контент (для RAG / NLP)
                "overview": m.get("overview"),

                # временные признаки
                "release_date": m.get("release_date"),
                "year": (m.get("release_date") or "")[:4] if m.get("release_date") else None,

                # числовые сигналы качества
                "vote_average": m.get("vote_average"),
                "vote_count": m.get("vote_count"),
                "popularity": m.get("popularity"),

                # классификация
                "original_language": m.get("original_language"),
                "adult": m.get("adult"),

                # мультимедиа
                "poster_path": m.get("poster_path"),
                "backdrop_path": m.get("backdrop_path"),

                # enrichment-ready (важно для следующего слоя)
                "genre_ids": m.get("genre_ids"),

                # system metadata
                "source": "tmdb"
            })

    return pl.DataFrame(rows)


if __name__ == '__main__':
    data = extract_tmdb_raw()
    print(len(data))


