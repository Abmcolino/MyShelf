# src/pages/readings.py
import pandas as pd
import os
import requests
from dash import html, dcc, dash_table
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output
import plotly.express as px

BOOKS_READ_CSV = "leidos.csv"


# ---------------------------------------------------------
# FUNCIÓN PARA CONSEGUIR PORTADA DE GOOGLE BOOKS
# ---------------------------------------------------------
def fetch_cover_image(title=None, authors=None):
    """Devuelve URL de portada o None si no existe."""
    if not title:
        return None

    q = f"intitle:{title}"
    if authors:
        q += f"+inauthor:{authors}"

    url = "https://www.googleapis.com/books/v1/volumes"
    params = {"q": q}

    try:
        r = requests.get(url, params=params, timeout=4)
        data = r.json()

        items = data.get("items")
        if not items:
            return None

        info = items[0].get("volumeInfo", {})
        links = info.get("imageLinks", {})

        # De mejor a peor calidad
        for key in ["extraLarge", "large", "medium", "thumbnail"]:
            if key in links:
                return links[key]

        return None
    except:
        return None


# ---------------------------------------------------------
# LAYOUT
# ---------------------------------------------------------
def readings_layout():

    if os.path.exists(BOOKS_READ_CSV):
        df = pd.read_csv(BOOKS_READ_CSV)
    else:
        df = pd.DataFrame(columns=['title','authors','categories','published_year','Date of reading'])

    df = df.drop(columns=['isbn13'], errors='ignore')

    return html.Div([
        html.H2("Mis Lecturas"),
        html.P("Lista de libros leídos (leidos.csv). Haz clic para ver detalles."),

        # ------------------------------
        # TABLA
        # ------------------------------
        dash_table.DataTable(
            id='readings-table',
            columns=[{"name": c, "id": c} for c in df.columns],
            data=df.to_dict('records'),
            page_size=20,
            filter_action="native",
            sort_action="native",
            row_selectable="single",
            style_table={'overflowX': 'auto', 'maxHeight': '400px', 'overflowY': 'scroll'},
            style_cell={
                'textAlign': 'left',
                'minWidth': '120px',
                'maxWidth': '250px',
                'whiteSpace': 'normal'
            },
            style_header={'backgroundColor': '#6d4c41', 'color': 'white', 'fontWeight': 'bold'},
            style_data={'backgroundColor': '#fefefe', 'color': '#3b2f2f', 'border': '1px solid #ddd'}
        ),

        html.Br(),

        # ------------------------------
        # TARJETA DEL LIBRO
        # ------------------------------
        html.Div(id="reading-card", className="mt-4"),

        html.Hr(),
        html.H3("Análisis de tus lecturas"),

        # ------------------------------
        # GRÁFICOS
        # ------------------------------
        dcc.Loading(id="loading-charts", children=[
            dcc.Graph(id='chart-year'),
            dcc.Graph(id='chart-category'),
            dcc.Graph(id='chart-time'),
            dcc.Graph(id='chart-authors')
        ], type="circle"),
    ])


# ---------------------------------------------------------
# CALLBACKS
# ---------------------------------------------------------
def register_readings_callbacks(app):

    # -------------------------
    # CALLBACK TARJETA
    # -------------------------
    @app.callback(
        Output("reading-card", "children"),
        Input("readings-table", "selected_rows"),
        Input("readings-table", "data")
    )
    def display_book_card(selected, rows):
        if not selected:
            return ""

        row = rows[selected[0]]

        title = row.get("title", "")
        authors = row.get("authors", "")
        categories = row.get("categories", "")
        year = row.get("published_year", "")
        date = row.get("Date of reading", "")

        # Buscar portada
        img_url = fetch_cover_image(title=title, authors=authors)

        # Card bonita
        return dbc.Card([
            dbc.Row([
                # Imagen solo si existe
                dbc.Col(
                    html.Img(src=img_url, style={"width": "100%", "borderRadius": "10px"}) if img_url else html.Div(),
                    width=3
                ),
                dbc.Col([
                    html.H4(title, className="card-title"),
                    html.P(f"👤 Autor(es): {authors}"),
                    html.P(f"🏷 Categorías: {categories}"),
                    html.P(f"📅 Año de publicación: {year}"),
                    html.P(f"📖 Fecha leída: {date}"),
                ], width=9)
            ], className="g-3"),

        ], body=True, style={"backgroundColor": "#f3e5ab", "borderRadius": "12px"})

    # -------------------------
    # CALLBACK GRÁFICOS
    # -------------------------
    @app.callback(
        Output('chart-year', 'figure'),
        Output('chart-category', 'figure'),
        Output('chart-time', 'figure'),
        Output('chart-authors', 'figure'),
        Input('chart-year', 'id')
    )
    def update_charts(_):
        if os.path.exists(BOOKS_READ_CSV):
            df = pd.read_csv(BOOKS_READ_CSV)
        else:
            df = pd.DataFrame(columns=['title','authors','categories','published_year','Date of reading'])

        # --- GRÁFICO POR AÑO ---
        fig_year = px.histogram(
            df, x='published_year', nbins=20,
            title='Libros leídos por año de publicación',
            color_discrete_sequence=px.colors.qualitative.Pastel
        )

        # --- CATEGORÍAS ---
        if 'categories' in df.columns:
            cats = df['categories'].dropna().str.split(',', expand=True).stack().str.strip()
            df_cat = cats.value_counts().reset_index()
            df_cat.columns = ["Category", "Count"]
            fig_cat = px.bar(df_cat, x="Category", y="Count", title="Libros por categoría")
        else:
            fig_cat = px.bar(title="Libros por categoría")

        # --- TIEMPO ---
        df['Date of reading'] = pd.to_datetime(df['Date of reading'], errors='coerce')
        df_time = df.groupby(df['Date of reading'].dt.date).size().reset_index(name='Count')
        fig_time = px.line(df_time, x='Date of reading', y='Count', title='Lecturas a lo largo del tiempo', markers=True)

        # --- AUTORES ---
        df_auth = df['authors'].value_counts().reset_index()
        df_auth.columns = ["Author", "Count"]
        fig_authors = px.bar(df_auth.head(10), x="Author", y="Count", title='Top autores más leídos')

        return fig_year, fig_cat, fig_time, fig_authors
