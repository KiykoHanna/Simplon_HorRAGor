# HorRAGor BOT Partie 1
---

L'objectif de ce projet est de concevoir HorRAGor (ou GorRAGor), un agent conversationnel spécialisé dans l'univers de l'horreur (cinéma, littérature, jeux vidéo). Pour que cet agent soit pertinent et évite les hallucinations, il doit s'appuyer sur une base de connaissances hybride, riche et parfaitement structurée.

## Ingestion Multimodale et Pipeline de Données Massives

# Pipeline d'Ingestion des Données

## Objectif

Cette première étape du projet HorRAGor consiste à construire une couche d'ingestion capable de collecter des données issues de plusieurs sources hétérogènes liées à l'univers du cinéma d'horreur. Ces données serviront de fondation à la future architecture RAG (Retrieval-Augmented Generation).

## Sources de données intégrées

### TMDB (The Movie Database)

Extraction des films d'horreur via l'API TMDB.

Données récupérées :

* Identifiants TMDB
* Titres et titres originaux
* Résumés (overview)
* Dates de sortie
* Popularité
* Notes et nombre de votes
* Langue d'origine
* Informations multimédias (posters, backdrops)

### IMDb

Utilisation des dumps officiels IMDb au format TSV.

Données récupérées :

* Films de type *movie*
* Films appartenant au genre *Horror*
* Année de sortie
* Genres
* Distribution principale (acteurs et actrices)

### Rotten Tomatoes

Collecte automatisée via Selenium.

Données récupérées :

* Tomatometer Score
* Audience Score
* Critics Consensus

### Kaggle Movies Dataset

Téléchargement automatisé du dataset *The Movies Dataset*.

Données récupérées :

* Titres
* Synopsis
* Taglines
* Genres
* Dates de sortie
* Popularité
* Notes utilisateurs

### MovieLens 1M

Téléchargement et intégration du dataset MovieLens.

Données récupérées :

* Films
* Genres
* Notes utilisateurs

Des agrégations sont calculées afin d'obtenir :

* Note moyenne
* Nombre total d'évaluations

## Technologies utilisées

* Python
* Polars
* PySpark
* Selenium
* Requests
* SQLite
* Kaggle API

## Architecture du Pipeline

Le pipeline de données est organisé selon une architecture ETL moderne permettant de préparer un corpus de qualité pour les futures étapes de Retrieval-Augmented Generation (RAG).

### 1. Ingestion

Collecte automatisée des données depuis plusieurs sources :

* TMDB API
* IMDb Datasets
* Rotten Tomatoes (Selenium Scraping)
* Kaggle Movies Dataset
* MovieLens 1M

Les données brutes sont stockées dans le dossier :

```text
data/raw/
```

### 2. Normalisation

Chaque source possède son propre module de normalisation.

Objectifs :

* Harmonisation des schémas de données
* Uniformisation des noms de colonnes
* Conversion des types de données
* Extraction des années de sortie
* Ajout d'informations de provenance (`source`)

Modules :

```text
src/normalization/
├── n_tmdb.py
├── n_imdb.py
├── n_kaggle.py
├── n_movielens.py
└── n_rotten.py
```

### 3. Cleaning

Nettoyage et validation des données.

Opérations réalisées :

* Suppression des doublons
* Validation des identifiants
* Suppression des titres vides
* Contrôle des années de sortie
* Validation des notes et scores
* Génération d'une clé normalisée (`title_key`)

Les jeux de données nettoyés sont enregistrés dans :

```text
data/processed/
```

Formats générés :

* Parquet (analyse et traitement)
* CSV (contrôle manuel)

### 4. Matching & Entity Resolution

Les données provenant de différentes sources sont fusionnées afin d'identifier les films correspondant à une même entité.

Méthodes utilisées :

#### Exact Matching

Correspondance basée sur :

* title_key
* year

#### Fuzzy Matching

Utilisation de RapidFuzz afin de détecter les correspondances proches entre les titres :

Exemples :

* The Shining ↔ The Shining (1980)
* IT ↔ It
* Halloween ↔ Halloween (1978)

Cette étape permet de réduire les doublons entre les différentes bases de données.

### 5. Construction du Gold Dataset

Création d'une table consolidée contenant :

* TMDB
* IMDb
* Kaggle
* MovieLens

Chaque film reçoit un identifiant interne :

```text
master_id
```

Le Gold Dataset constitue la source de vérité du projet.

### 6. Enrichment Layer

Après la fusion des données principales, un enrichissement est réalisé à partir de Rotten Tomatoes.

Informations ajoutées :

* Tomatometer Score
* Audience Score
* Critics Consensus

Cette couche est séparée du processus de matching afin de préserver l'intégrité des entités principales.

### 7. Base de données (Supabase)
Rôle dans le projet

Supabase est utilisé comme couche de persistance finale (Gold Layer) du pipeline ETL.
Le dataset gold_movies représente la version unifiée, nettoyée et dédupliquée des données issues de plusieurs sources.

Table principale : movies_gold

La table contient un enregistrement unique par film, identifié par master_id (PRIMARY KEY).

Exemple de structure logique :

Identifiants : master_id, tmdb_id, imdb_id, movie_id

Métadonnées : title, original_title, overview, tagline

Qualité & scores : vote_average, vote_count, popularity, avg_rating

Genres & acteurs : genres, genre_ids, actors

Sources : source, source_imdb, source_kaggle, source_ml

Enrichissement : url, tomatometer_score, audience_score


## 8. Structure du projet

```text
src/
├── ingestion/
├── normalization/
├── cleaning/
├── matching/
├── merging/
└── enrichment/

database/
├── connection.py
└── load_gold.py

data/
├── raw/
├── processed/
└── gold/

scripts/
├── main.py
```

---

### 9. Exécution et vérification de la base de données (Supabase)

1. Prérequis

Avant de lancer le projet, vérifier :
- Installation des dépendances 
    - uv sync
- Variables d’environnement 

```text
TMDB_API_KEY=9f9934a1803dfed644f1be14add420d0

TMDB_URL="https://api.themoviedb.org/3"

SUPABASE_URL="https://pghaqpdcdvfrwbhcgksl.supabase.co"
SUPABASE_KEY="sb_publishable__QdCTceUQQvkIScuerrT9Q_dRFmPr_v"
```

2. Lancement du pipeline ETL

```python
python -m scripts.main
```
Le pipeline exécute les étapes suivantes :

- Vérification / création des données nettoyées (processed/)
- Construction du dataset gold (gold/)
- Chargement des données dans Supabase

3. Vérification des données locales

Données traitées (processed)

Chemin : data/processed/

Fichiers attendus :

- tmdb_clean.parquet
- imdb_clean.parquet
- kaggle_clean.parquet
- movielens_clean.parquet

Dataset final (gold)

Chemin : data/gold/

Fichier attendu :

- gold_movies.parquet

4. Vérification dans Supabase

Vérifier le nombre de lignes

Dans le SQL Editor :
```sql
SELECT COUNT(*) FROM movies;
```
```sql
SELECT master_id, COUNT(*)
FROM movies_gold
GROUP BY master_id
HAVING COUNT(*) > 1;
SELECT COUNT(*) FROM movies;
```