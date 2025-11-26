# src/pages/readings.py
import pandas as pd
import os
import requests
from dash import html, dcc, Input, Output
import dash_bootstrap_components as dbc
import plotly.express as px

BOOKS_READ_CSV = "leidos.csv"

# ---------------------------------------------------------
# FUNCIÓN PARA CONSEGUIR PORTADA DE GOOGLE BOOKS
# ---------------------------------------------------------
def fetch_cover_image(title=None, authors=None):
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
            style_cell={'textAlign': 'left', 'minWidth': '120px', 'maxWidth': '250px', 'whiteSpace': 'normal'},
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
        # CHECKLIST DE GRÁFICOS
        # ------------------------------
        dbc.Row([
            dbc.Col([
                html.Label("Selecciona las gráficas a mostrar:"),
                dcc.Checklist(
                    id='graph-select',
                    options=[
                        {'label':'Libros por año de publicación','value':'year'},
                        {'label':'Top 10 Categorías','value':'categories'},
                        {'label':'Lecturas a lo largo del tiempo','value':'time'},
                        {'label':'Top 10 Autores','value':'authors'}
                    ],
                    value=['year','categories','time','authors'],
                    inline=False
                ),
                html.Br(),
                dbc.Button("Mostrar", id='show-graphs-btn', color='primary')
            ], width=3),
            dbc.Col(html.Div(id='graphs-container'), width=9)
        ])
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
        img_url = fetch_cover_image(title=title, authors=authors)
        return dbc.Card([
            dbc.Row([
                dbc.Col(html.Img(src=img_url, style={"width": "100%", "borderRadius": "10px"}) if img_url else html.Div(), width=3),
                dbc.Col([
                    html.H4(title, className="card-title"),
                    html.P(f"👤 Autor(es): {authors}"),
                    html.P(f"🏷 Categorías: {categories}"),
                    html.P(f"📅 Año de publicación: {year}"),
                    html.P(f"📖 Fecha leída: {date}")
                ], width=9)
            ], className="g-3")
        ], body=True, style={"backgroundColor": "#f3e5ab", "borderRadius": "12px"})

    # -------------------------
    # CALLBACK GRÁFICOS
    # -------------------------
    @app.callback(
        Output('graphs-container', 'children'),
        Input('show-graphs-btn', 'n_clicks'),
        Input('graph-select', 'value'),
        prevent_initial_call=True
    )
    def update_graphs(n_clicks, selected_graphs):
        if os.path.exists(BOOKS_READ_CSV):
            df = pd.read_csv(BOOKS_READ_CSV)
        else:
            df = pd.DataFrame(columns=['title','authors','categories','published_year','Date of reading'])

        df['published_year'] = pd.to_numeric(df.get('published_year', pd.Series()), errors='coerce').fillna(0)
        df['Date of reading'] = pd.to_datetime(df.get('Date of reading', pd.Series()), errors='coerce')
        df.fillna({'title':'Desconocido','authors':'Desconocido','categories':'Sin categoría'}, inplace=True)

        if df.empty:
            return [html.P("Todavía no hay libros leídos para mostrar estadísticas.")]

        children = []

        if 'year' in selected_graphs:
            fig = px.histogram(df, x='published_year', nbins=20,
                               title="Libros por año de publicación",
                               color_discrete_sequence=['#D35400'])
            children.append(dbc.Card(dbc.CardBody(dcc.Graph(figure=fig)),
                                     className='mb-3 shadow-sm', style={'backgroundColor':'#FFF3E0'}))

        if 'categories' in selected_graphs:
            df['categories_list'] = df['categories'].fillna('').apply(lambda x: [c.strip() for c in x.split(',') if c])
            all_categories = [c for sublist in df['categories_list'] for c in sublist]
            top_categories = pd.Series(all_categories).value_counts().nlargest(10)
            fig = px.bar(x=top_categories.index, y=top_categories.values,
                         title="Top 10 Categorías",
                         color_discrete_sequence=['#A04000'])
            children.append(dbc.Card(dbc.CardBody(dcc.Graph(figure=fig)),
                                     className='mb-3 shadow-sm', style={'backgroundColor':'#FFF3E0'}))

        if 'time' in selected_graphs:
            df_time = df.groupby(df['Date of reading'].dt.date).size().reset_index(name='Count')
            fig = px.line(df_time, x='Date of reading', y='Count',
                          title='Lecturas a lo largo del tiempo', markers=True,
                          color_discrete_sequence=['#D35400'])
            children.append(dbc.Card(dbc.CardBody(dcc.Graph(figure=fig)),
                                     className='mb-3 shadow-sm', style={'backgroundColor':'#FFF3E0'}))

        if 'authors' in selected_graphs:
            top_authors = df['authors'].value_counts().nlargest(10)
            fig = px.bar(x=top_authors.index, y=top_authors.values,
                         title='Top 10 Autores',
                         color_discrete_sequence=['#D35400'])
            children.append(dbc.Card(dbc.CardBody(dcc.Graph(figure=fig)),
                                     className='mb-3 shadow-sm', style={'backgroundColor':'#FFF3E0'}))

        return children
