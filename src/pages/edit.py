# src/pages/edit.py
from dash import html, dcc
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
import pandas as pd
from src.etl import load_books, save_books

def edit_form_layout():
    return html.Div([
        html.H2("Añadir un nuevo libro"),
        html.P("Rellena los campos y pulsa 'Guardar' para añadir el libro a la base de datos."),

        dbc.Row([
            dbc.Col([
                dbc.Label("Título"),
                dbc.Input(id='input-title', type='text', placeholder='Título del libro'),
            ], width=6),
            dbc.Col([
                dbc.Label("Autores"),
                dbc.Input(id='input-authors', type='text', placeholder='Nombre de los autores'),
            ], width=6),
        ], className='mb-2'),

        dbc.Row([
            dbc.Col([
                dbc.Label("Categorías"),
                dbc.Input(id='input-categories', type='text', placeholder='Ej: Aventura, Fantasía'),
            ], width=4),
            dbc.Col([
                dbc.Label("Año de publicación"),
                dbc.Input(id='input-year', type='number', placeholder='Año de publicación'),
            ], width=4),
            dbc.Col([
                dbc.Label("Valoración media"),
                dbc.Input(id='input-rating', type='number', placeholder='0-5', min=0, max=5, step=0.1),
            ], width=4),
        ], className='mb-2'),

        dbc.Button("Guardar libro", id='save-book-btn', color='primary', className='mt-2'),
        html.Div(id='save-book-result', className='mt-2')
    ])


def register_edit_callbacks(app):
    @app.callback(
        Output('save-book-result', 'children'),
        Input('save-book-btn', 'n_clicks'),
        State('input-title', 'value'),
        State('input-authors', 'value'),
        State('input-categories', 'value'),
        State('input-year', 'value'),
        State('input-rating', 'value'),
        prevent_initial_call=True
    )
    def save_book(n_clicks, title, authors, categories, year, rating):
        if not title:
            return dbc.Alert("El título es obligatorio.", color='warning')

        df = load_books()
        new_entry = {
            'title': title,
            'authors': authors or '',
            'categories': categories or '',
            'published_year': int(year) if year else None,
            'average_rating': float(rating) if rating else None
        }
        df = pd.concat([df, pd.DataFrame([new_entry])], ignore_index=True)
        save_books(df)

        return dbc.Alert(f"Libro '{title}' añadido correctamente.", color='success')
