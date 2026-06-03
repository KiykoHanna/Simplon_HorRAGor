# src/ingestion/rotten_scraper.py

import time
import re
import polars as pl

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class RottenTomatoesScraper:
    def __init__(self, headless: bool = False):
        options = Options()
        if headless:
            options.add_argument("--headless=new")

        options.add_argument("--window-size=1920,1080")
        options.add_argument("--disable-blink-features=AutomationControlled")

        self.driver = webdriver.Chrome(options=options)
        self.wait = WebDriverWait(self.driver, 10)

    def close(self):
        self.driver.quit()

    # --- slug builder ---
    def _build_slug(self, title: str) -> str:
        title = title.lower()
        title = re.sub(r"[^\w\s]", "", title)
        return re.sub(r"\s+", "_", title.strip())

    # --- scrape single movie ---
    def scrape_movie(self, title: str) -> dict:
        slug = self._build_slug(title)
        url = f"https://www.rottentomatoes.com/m/{slug}"

        result = {
            "title": title,
            "tomatometer_score": None,
            "audience_score": None,
            "critics_consensus": None,
            "url": url,
            "source": "rotten_tomatoes"
        }

        try:
            self.driver.get(url)

            self.wait.until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )

            time.sleep(2)

            # --- Tomatometer ---
            try:
                val = self.driver.find_element(
                    By.CSS_SELECTOR, '[data-qa="tomatometer-score"]'
                ).text
                result["tomatometer_score"] = int(re.sub(r"\D", "", val))
            except:
                pass

            # --- Audience ---
            try:
                val = self.driver.find_element(
                    By.CSS_SELECTOR, '[data-qa="audience-score"]'
                ).text
                result["audience_score"] = int(re.sub(r"\D", "", val))
            except:
                pass

            # --- Consensus ---
            try:
                val = self.driver.find_element(
                    By.CSS_SELECTOR, '[data-qa="critics-consensus"]'
                ).text
                result["critics_consensus"] = val.strip()
            except:
                pass

        except Exception as e:
            print(f"[ERROR] {title} → {e}")

        return result


# ETL LAYER ---------------------------

def extract_rotten_tomatoes(movies: list[str]) -> list[dict]:
    
    print("extract RT...")
    scraper = RottenTomatoesScraper(headless=False)
    
    rows = []

    for title in movies:
        try:
            rows.append(scraper.scrape_movie(title))
        except Exception as e:
            print(f"error {title}:", e)

    scraper.close()  
    return pl.DataFrame(rows, orient="row")


# MAIN (FIXED) ---------------------------

if __name__ == "__main__":

    movies = [
        "The Shining",
        "It",
        "The Conjuring"
    ]
    rows = extract_rotten_tomatoes(movies)


