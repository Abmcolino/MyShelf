# src/pages/resenas.py
import pandas as pd
import os
from dash import html, dcc, Input, Output, State, callback_context
import dash_bootstrap_components as dbc
from datetime import datetime

LEIDOS_CSV = "leidos.csv"
RESEÑAS_CSV = "reseñas.csv"

# ---------------------------
# Layout
# ---------------------------
def reseñas_layout():
    # cargar libros leídos
    if os.path.exists(LEIDOS_CSV):
        df_books = pd.read_csv(LEIDOS_CSV)
    else:
        df_books = pd.DataFrame(columns=['isbn13', 'title'])

    options_books = [{'label': r['title'], 'value': r['isbn13']} for _, r in df_books.iterrows()]

    layout = html.Div([
        html.H2("Reseñas de libros"),
        html.Hr(),

        # Formulario para añadir reseña
        dbc.Row([
            dbc.Col([
                html.Label("Selecciona un libro"),
                dcc.Dropdown(id='reseña-book-dropdown', options=options_books, placeholder="Elige un libro")
            ], md=4),
            dbc.Col([
                html.Label("Escribe tu reseña"),
                dcc.Textarea(id='reseña-text', placeholder="Tu reseña aquí...", style={'width':'100%'})
            ], md=4),
            dbc.Col([
                html.Label("Nota"),
                dcc.Slider(id='reseña-rating', min=1, max=5, step=1, marks={i:str(i) for i in range(1,6)}, value=5),
                html.Br(),
                dbc.Button("Añadir reseña", id='add-review-btn', color='primary')
            ], md=4),
        ], className='mb-4'),

        # Selector de orden
        dbc.Row([
            dbc.Col([
                html.Label("Ordenar por"),
                dcc.Dropdown(
                    id='orden-select',
                    options=[
                        {'label':'Fecha (más reciente primero)','value':'fecha'},
                        {'label':'Nota (mayor primero)','value':'nota'}
                    ],
                    value='fecha',
                    clearable=False
                )
            ], md=4)
        ], className='mb-3'),

        # Contenedor de reseñas
        dbc.Row([
            dbc.Col(html.Div(id='reseñas-list'), width=12)
        ])
    ])

    return layout

# ---------------------------
# Callbacks
# ---------------------------
def register_reseñas_callbacks(app):

    @app.callback(
        Output('reseñas-list', 'children'),
        Input('add-review-btn', 'n_clicks'),
        Input('orden-select', 'value'),
        State('reseña-book-dropdown', 'value'),
        State('reseña-text', 'value'),
        State('reseña-rating', 'value'),
        prevent_initial_call=True
    )
    def update_reviews(n_clicks, orden, book, text, rating):
        ctx = callback_context
        triggered_id = ctx.triggered[0]['prop_id'].split('.')[0]

        # si se pulsa el botón de añadir reseña
        if triggered_id == 'add-review-btn':
            if not book or not text or not rating:
                return [dbc.Alert("Debes rellenar todos los campos.", color='warning')]

            # obtener título del libro
            if os.path.exists(LEIDOS_CSV):
                df_books = pd.read_csv(LEIDOS_CSV)
                title = df_books[df_books['isbn13']==book]['title'].values[0]
            else:
                title = "Libro desconocido"

            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            entry = {
                'isbn13': book,
                'book': title,
                'reseña': text,
                'nota': rating,
                'fecha': now
            }

            if os.path.exists(RESEÑAS_CSV):
                df_res = pd.read_csv(RESEÑAS_CSV)
                df_res = pd.concat([df_res, pd.DataFrame([entry])], ignore_index=True)
            else:
                df_res = pd.DataFrame([entry])
            df_res.to_csv(RESEÑAS_CSV, index=False)

        # leer reseñas y ordenarlas
        if os.path.exists(RESEÑAS_CSV):
            df_res = pd.read_csv(RESEÑAS_CSV)
        else:
            df_res = pd.DataFrame()

        if df_res.empty:
            return [html.P("Todavía no hay reseñas disponibles.")]

        # ordenar
        if orden == 'nota':
            df_res = df_res.sort_values('nota', ascending=False)
        else:
            df_res = df_res.sort_values('fecha', ascending=False)

        # crear tarjetas 3x3
        cards = []
        for _, r in df_res.iterrows():
            cards.append(
                dbc.Col(
                    dbc.Card([
                        dbc.CardHeader(f"{r['book']} — {r['nota']}/5"),
                        dbc.CardBody(r['reseña'])
                    ], className='mb-3 shadow-sm'),
                    md=4
                )
            )

        # distribuir en filas de 3
        rows = []
        for i in range(0, len(cards), 3):
            rows.append(dbc.Row(cards[i:i+3], className='mb-3'))

        return rows
