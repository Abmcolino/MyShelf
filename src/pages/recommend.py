# src/pages/recommend.py
import pandas as pd
from dash import html, dcc
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.neighbors import NearestNeighbors
from sklearn.preprocessing import MinMaxScaler
import numpy as np

from src.etl import load_books


# Modelo global
MODEL = None
FEATURE_MATRIX = None
DF_BOOKS = None
TFIDF = None
SCALER = None


# -------------------------------------------------------
# 📚 OBTENER PORTADA DESDE OPENLIBRARY
# -------------------------------------------------------
def get_cover_url(isbn):
    """
    Devuelve la URL de la portada usando OpenLibrary.
    Si no hay ISBN → devuelve portada por defecto.
    """
    if isbn and isinstance(isbn, str):
        isbn_clean = isbn.replace("-", "").strip()
        return f"https://covers.openlibrary.org/b/isbn/{isbn_clean}-M.jpg"

    # fallback
    return "https://via.placeholder.com/128x195.png?text=No+Cover"


# -------------------------------------------------------
# 🔧 ENTRENAR MODELO
# -------------------------------------------------------
def train_model():
    global MODEL, FEATURE_MATRIX, DF_BOOKS, TFIDF, SCALER

    df = load_books().copy()
    DF_BOOKS = df

    df["meta"] = (
        df["authors"].fillna("") + " " +
        df["categories"].fillna("") + " " +
        df["title"].fillna("")
    )

    # TFIDF
    TFIDF = TfidfVectorizer(stop_words="english")
    X_text = TFIDF.fit_transform(df["meta"])

    # Numéricas
    num_features = df[["published_year", "average_rating"]].fillna(0)
    SCALER = MinMaxScaler()
    X_num = SCALER.fit_transform(num_features)

    FEATURE_MATRIX = np.hstack([X_text.toarray(), X_num])

    MODEL = NearestNeighbors(n_neighbors=10, metric="cosine")
    MODEL.fit(FEATURE_MATRIX)


# -------------------------------------------------------
# 🎯 RECOMENDACIÓN
# -------------------------------------------------------
def recommend_books(preferred_categories, min_rating, year_from):
    global DF_BOOKS, MODEL, FEATURE_MATRIX, TFIDF, SCALER

    df = DF_BOOKS.copy()

    # Texto del usuario basado en géneros elegidos
    if preferred_categories:
        user_text = " ".join(preferred_categories)
    else:
        user_text = ""

    X_user_text = TFIDF.transform([user_text]).toarray()

    # Numéricas
    year = int(year_from) if year_from else 0
    rating = float(min_rating) if min_rating else 0

    X_user_num = np.array([[year, rating]])
    X_user_num_scaled = SCALER.transform(X_user_num)

    # Vector final
    X_user = np.hstack([X_user_text, X_user_num_scaled])

    distances, indices = MODEL.kneighbors(X_user)
    recs = df.iloc[indices[0]].copy()
    recs["distance"] = distances[0]

    return recs.head(6)


# -------------------------------------------------------
# 🎨 LAYOUT
# -------------------------------------------------------
def recommend_layout():
    if MODEL is None:
        train_model()

    df = DF_BOOKS.copy()

    # -------------------------------------------------------
    # 📊 ORDENAR CATEGORÍAS POR FRECUENCIA
    # -------------------------------------------------------
    category_counts = {}

    for row in df["categories"].dropna():
        for cat in row.split(","):
            c = cat.strip()
            if c:
                category_counts[c] = category_counts.get(c, 0) + 1

    # Ordenadas por frecuencia descendente
    all_categories = [
        c for c, _ in sorted(category_counts.items(), key=lambda x: x[1], reverse=True)
    ]
    # -------------------------------------------------------

    return html.Div([

        html.H2("🔮 Recomendador Inteligente de Libros", className="mb-4"),

        dbc.Row([
            dbc.Col([
                dbc.Label("Selecciona tus géneros favoritos"),
                dcc.Dropdown(
                    id="rec-category",
                    options=[{"label": c, "value": c} for c in all_categories],
                    multi=True,
                    placeholder="Ej: Fantasía, Misterio, Romance"
                )
            ], width=6),

            dbc.Col([
                dbc.Label("Valoración mínima"),
                dbc.Input(id="rec-min-rating", type="number",
                          min=0, max=5, step=0.1, placeholder="Ej: 3.5")
            ], width=3),

            dbc.Col([
                dbc.Label("A partir de año"),
                dbc.Input(id="rec-year-from", type="number",
                          placeholder="Ej: 2000")
            ], width=3)
        ], className="mb-3"),

        dbc.Button("Recomendar libros", id="rec-btn", color="primary"),

        html.Div(id="rec-results", className="mt-4")
    ])
# -------------------------------------------------------
# 🔁 CALLBACK
# -------------------------------------------------------
def register_callbacks(app):
    @app.callback(
        Output("rec-results", "children"),
        Input("rec-btn", "n_clicks"),
        State("rec-category", "value"),
        State("rec-min-rating", "value"),
        State("rec-year-from", "value"),
        prevent_initial_call=True
    )
    def recommend_action(n, categories, rating, year):
        recs = recommend_books(categories, rating, year)

        cards = []
        for _, row in recs.iterrows():

            cover = get_cover_url(row.get("isbn", ""))

            card = html.Div(
                className="rec-card",
                children=[
                    html.Img(src=cover, className="rec-cover"),
                    html.H4(row["title"], className="rec-title"),
                    html.P(f"Autor: {row['authors']}", className="rec-author"),
                    html.P(f"Categorías: {row['categories']}", className="rec-cats"),
                    html.P(f"Rating: {row['average_rating']}", className="rec-rating"),
                ]
            )
            cards.append(card)

        return html.Div(className="cards-grid", children=cards)
