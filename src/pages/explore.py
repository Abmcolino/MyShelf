# src/pages/explore.py
import pandas as pd
import os
from dash import html, dcc, Input, Output
import dash_bootstrap_components as dbc
import plotly.express as px

LEIDOS_CSV = "leidos.csv"

def explore_layout():
    """
    Layout de exploración con checklist de gráficas y botón 'Mostrar'.
    """
    return html.Div([
        html.H2("📚 Exploración de la Biblioteca"),
        html.Hr(),
        dbc.Row([
            dbc.Col([
                html.Label("Selecciona las gráficas a mostrar:"),
                dcc.Checklist(
                    id='graph-select',
                    options=[
                        {'label':'Años de Publicación','value':'years'},
                        {'label':'Distribución de Nota Promedio','value':'ratings'},
                        {'label':'Top 10 Autores','value':'authors'},
                        {'label':'Top 10 Categorías','value':'categories'},
                        {'label':'Últimos libros leídos','value':'recent'},
                        {'label':'Promedio de nota por autor','value':'avg_auth'}
                    ],
                    value=['years','ratings','authors','categories','recent','avg_auth'],
                    inline=False
                ),
                html.Br(),
                dbc.Button("Mostrar", id='show-graphs-btn', color='primary')
            ], width=3),
            dbc.Col(html.Div(id='graphs-container'), width=9)
        ])
    ])

def register_explore_callbacks(app):
    """
    Callback para generar dinámicamente las gráficas según las seleccionadas.
    """
    @app.callback(
        Output('graphs-container', 'children'),
        Input('show-graphs-btn', 'n_clicks'),
        Input('graph-select', 'value'),
        prevent_initial_call=True
    )
    def update_graphs(n_clicks, selected_graphs):
        # Cargar CSV
        if os.path.exists(LEIDOS_CSV):
            df = pd.read_csv(LEIDOS_CSV)
        else:
            df = pd.DataFrame(columns=['title','authors','categories','published_year','nota','Date of reading'])

        # Normalizar columnas
        df['published_year'] = pd.to_numeric(df.get('published_year', pd.Series()), errors='coerce').fillna(0)
        df['nota'] = pd.to_numeric(df.get('nota', pd.Series()), errors='coerce').fillna(0)
        df['Date of reading'] = pd.to_datetime(df.get('Date of reading', pd.Series()), errors='coerce')
        df.fillna({'title':'Desconocido','authors':'Desconocido','categories':'Sin categoría'}, inplace=True)

        if df.empty:
            return [html.P("Todavía no hay libros leídos para mostrar estadísticas.")]

        # ---------- Crear figuras según selección ----------
        children = []

        if 'years' in selected_graphs:
            fig = px.histogram(df, x='published_year', nbins=20,
                               title="Años de Publicación",
                               color_discrete_sequence=['#D35400'])
            children.append(dbc.Card(dbc.CardBody(dcc.Graph(figure=fig)),
                                     className='mb-3 shadow-sm', style={'backgroundColor':'#FFF3E0'}))

        if 'ratings' in selected_graphs:
            fig = px.histogram(df, x='nota', nbins=5,
                               title="Distribución de Nota Promedio",
                               color_discrete_sequence=['#A04000'])
            children.append(dbc.Card(dbc.CardBody(dcc.Graph(figure=fig)),
                                     className='mb-3 shadow-sm', style={'backgroundColor':'#FFF3E0'}))

        if 'authors' in selected_graphs:
            top_authors = df['authors'].value_counts().nlargest(10)
            fig = px.bar(x=top_authors.index, y=top_authors.values,
                         title="Top 10 Autores",
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

        if 'recent' in selected_graphs:
            df_recent = df.sort_values('Date of reading', ascending=False).head(10)
            # Crear tarjetas individuales por libro
            row_cards = []
            for _, row in df_recent.iterrows():
                card = dbc.Col(
                    dbc.Card([
                        dbc.CardHeader(f"{row['title']} — {row['nota']}/5"),
                        dbc.CardBody([
                            html.P(f"Autor(es): {row['authors']}"),
                            html.P(f"Categorías: {row['categories']}"),
                            html.P(f"Fecha de lectura: {row['Date of reading'].date() if pd.notnull(row['Date of reading']) else 'Desconocido'}")
                        ])
                    ], style={'backgroundColor':'#FFF3E0'}, className='mb-3 shadow-sm'),
                    width=4
                )
                row_cards.append(card)
            # Distribuir tarjetas en filas de 3
            for i in range(0, len(row_cards), 3):
                children.append(dbc.Row(row_cards[i:i+3], className='mb-3'))

        if 'avg_auth' in selected_graphs:
            df_auth_avg = df.groupby('authors')['nota'].mean().sort_values(ascending=False).head(10)
            fig = px.bar(x=df_auth_avg.index, y=df_auth_avg.values,
                         title="Promedio de nota por autor",
                         color_discrete_sequence=['#D35400'])
            children.append(dbc.Card(dbc.CardBody(dcc.Graph(figure=fig)),
                                     className='mb-3 shadow-sm', style={'backgroundColor':'#FFF3E0'}))

        return children
