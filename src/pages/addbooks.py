# src/pages/add_books.py
import pandas as pd
from dash import html, dcc
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
from datetime import datetime
import os

BOOKS_CSV = "books.csv"
LEIDOS_CSV = "leidos.csv"

# -----------------------------
# 📚 CARGAR LIBROS
# -----------------------------
def load_books():
    return pd.read_csv(BOOKS_CSV)

# -----------------------------
# 📝 LAYOUT PARA AÑADIR LIBROS
# -----------------------------
def add_books_layout():
    df = load_books()

    # Limpiar filas con datos incompletos
    df = df.dropna(subset=['title', 'isbn13'])
    df['isbn13'] = df['isbn13'].astype(str)  # asegurar string

    options = [
        {'label': f"{r['title']} — {r.get('authors','')}", 'value': r['isbn13']}
        for _, r in df.iterrows()
    ]

    return html.Div([
        html.H2("Añadir libros leídos"),
        html.P("Busca un libro y márcalo como leído."),
        dcc.Dropdown(
            id='add-book-dropdown',
            options=options,
            placeholder="Busca un libro...",
            searchable=True,
            style={'margin-bottom':'10px'}
        ),
        dbc.Button("Marcar como leído", id='add-book-btn', color='success', className='mb-2'),
        html.Div(id='add-book-result')
    ])

# -----------------------------
# 🔁 CALLBACK PARA AÑADIR LIBROS
# -----------------------------
def register_add_books_callbacks(app):

    @app.callback(
        Output('add-book-result', 'children'),
        Input('add-book-btn', 'n_clicks'),
        State('add-book-dropdown', 'value'),
        prevent_initial_call=True
    )
    def add_book(n_clicks, isbn):
        if not isbn:
            return dbc.Alert("Debes seleccionar un libro.", color='warning')

        df = load_books()
        df = df.dropna(subset=['isbn13'])
        df['isbn13'] = df['isbn13'].astype(str)

        book = df[df['isbn13'] == str(isbn)].iloc[0]
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        entry = {
            'isbn13': book['isbn13'],
            'title': book['title'],
            'authors': book.get('authors',''),
            'categories': book.get('categories',''),
            'published_year': book.get('published_year',''),
            'Date of reading': now
        }

        # Guardar en leidos.csv
        if os.path.exists(LEIDOS_CSV):
            df_existing = pd.read_csv(LEIDOS_CSV)
            df_existing = pd.concat([df_existing, pd.DataFrame([entry])], ignore_index=True)
        else:
            df_existing = pd.DataFrame([entry])

        df_existing.to_csv(LEIDOS_CSV, index=False)

        return dbc.Alert(f"'{book['title']}' ha sido añadido a tus libros leídos.", color='success')
