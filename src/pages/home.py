# src/pages/home.py
import random
import pandas as pd
from dash import html, dcc
import openai
import os

# ---- Configura tu API Key de OpenAI ----
openai.api_key = os.getenv("OPENAI_API_KEY")  # Debes tener la variable de entorno configurada

# ---- Función para generar reseña con GPT ----
def generate_review(title, author):
    """
    Genera una reseña breve y persuasiva usando GPT sobre por qué leer el libro.
    """
    prompt = f"Escribe una reseña breve y persuasiva sobre por qué leer el libro '{title}' de {author}. Máximo 50 palabras."

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",  # o "gpt-3.5-turbo"
            messages=[
                {"role": "system", "content": "Eres un experto recomendador de libros."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=80,
            temperature=0.7
        )
        review_text = response['choices'][0]['message']['content'].strip()
        return review_text
    except Exception as e:
        # Fallback si falla la API
        return f"'{title}' de {author} es un libro fascinante que vale la pena leer."

# ---- Carga libros desde CSV ----
def load_books():
    df = pd.read_csv("books.csv")  # Ajusta la ruta si es distinta

    # Detectar columnas posibles de título y autor
    title_cols = ['title', 'Title', 'titulo', 'Título', 'book_title']
    author_cols = ['author', 'Author', 'autor', 'Autor', 'writer', 'authors']

    for col in title_cols:
        if col in df.columns:
            title_col = col
            break
    else:
        raise ValueError("No se encontró columna de título en el CSV")

    for col in author_cols:
        if col in df.columns:
            author_col = col
            break
    else:
        raise ValueError("No se encontró columna de autor en el CSV")

    df['title_col'] = df[title_col]
    df['author_col'] = df[author_col]
    return df

# ---- Layout de Home con tarjetas ----
# ---- Layout de Home con tarjetas ----
def home_layout():
    df = load_books()

    # Filtra libros no leídos
    if 'read' in df.columns:
        df_unread = df[df['read'] != True]
    else:
        df_unread = df.copy()

    # Tomar exactamente 5 libros
    sample_books = df_unread.sample(n=min(5, len(df_unread)), random_state=42)

    # Crear tarjetas
    cards = []
    for _, row in sample_books.iterrows():
        title = row.get('title_col')
        author = row.get('author_col')
        review = generate_review(title, author)

        card = html.Div(
            className="book-card",
            children=[
                html.H4(title, className="book-title"),
                html.P(f"Autor: {author}", className="book-author"),
                html.Div(review, className="book-review hover-review")
            ]
        )
        cards.append(card)

    return html.Div(
        className="home-container",
        children=[
            html.H2("📚 Libros recomendados para ti", className="home-title"),
            html.Div(className="cards-grid cards-grid-home", children=cards)
        ]
    )
    df = load_books()

    # Filtra libros que no se han leído aún
    if 'read' in df.columns:
        df_unread = df[df['read'] != True]
    else:
        df_unread = df.copy()  # Si no hay columna 'read', toma todos

    # Elige aleatoriamente 6 libros
    sample_books = df_unread.sample(n=min(6, len(df_unread)), random_state=42)

    # Crear tarjetas
    cards = []
    for _, row in sample_books.iterrows():
        title = row.get('title_col')
        author = row.get('author_col')
        review = generate_review(title, author)

        card = html.Div(
            className="book-card",
            children=[
                html.H4(title, className="book-title"),
                html.P(f"Autor: {author}", className="book-author"),
                html.Div(review, className="book-review hover-review")
            ]
        )
        cards.append(card)

    return html.Div(
        className="home-container",
        children=[
            html.H2("📚 Libros recomendados para ti", className="home-title"),
            html.Div(className="cards-grid", children=cards)
        ]
    )
