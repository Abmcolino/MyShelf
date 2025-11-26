import pandas as pd
import os

BOOKS_CSV = os.path.join(os.path.dirname(os.path.dirname(__file__)), "books.csv")
RATINGS_CSV = os.path.join(os.path.dirname(os.path.dirname(__file__)), "ratings.csv")

def load_books(nrows=None):
    """Carga el CSV de libros y hace limpieza básica."""
    df = pd.read_csv(BOOKS_CSV, low_memory=False, nrows=nrows)
    # Normalizar nombres de columnas comunes (ajusta si tu CSV difiere)
    cols = {c.lower(): c for c in df.columns}
    # asegurar columnas mínimas
    # crear columnas si faltan
    for c in ["isbn13","isbn10","title","subtitle","authors","categories","thumbnail","description","published_year","average_rating"]:
        if c not in df.columns:
            df[c] = pd.NA
    # limpieza simple
    df['title'] = df['title'].fillna("Untitled").astype(str)
    df['authors'] = df['authors'].fillna("Unknown").astype(str)
    df['categories'] = df['categories'].fillna("Unknown").astype(str)
    # convertir published_year a int cuando sea posible
    try:
        df['published_year'] = pd.to_numeric(df['published_year'], errors='coerce').astype('Int64')
    except Exception:
        pass
    return df

def save_books(df):
    """Sobrescribe books.csv con el dataframe (precaución)."""
    df.to_csv(BOOKS_CSV, index=False)

def load_ratings():
    """Carga o crea archivo de ratings para tu sistema colaborativo."""
    if os.path.exists(RATINGS_CSV):
        return pd.read_csv(RATINGS_CSV)
    else:
        df = pd.DataFrame(columns=['user_id','isbn13','rating'])
        df.to_csv(RATINGS_CSV, index=False)
        return df

def save_ratings(df):
    df.to_csv(RATINGS_CSV, index=False)
