import plotly.express as px
import pandas as pd

def plot_publication_years(df, bins=20):
    df2 = df.dropna(subset=['published_year'])
    if df2.empty:
        return {}
    fig = px.histogram(df2, x='published_year', nbins=bins, title="Distribución de años de publicación")
    fig.update_layout(xaxis_title="Año", yaxis_title="Cantidad")
    return fig

def plot_average_rating_distribution(df):
    df2 = df.dropna(subset=['average_rating'])
    if df2.empty:
        return {}
    fig = px.histogram(df2, x='average_rating', nbins=20, title="Distribución de valoración media")
    fig.update_layout(xaxis_title="Valoración media", yaxis_title="Cantidad")
    return fig

def top_authors_bar(df, top_n=15):
    # autores pueden venir en strings con separadores; simplificamos tomando la celda completa
    s = df['authors'].fillna("Unknown")
    counts = s.value_counts().nlargest(top_n)
    fig = px.bar(x=counts.values, y=counts.index, orientation='h', title=f"Top {top_n} autores")
    fig.update_layout(xaxis_title="Libros", yaxis_title="Autor", height=400)
    return fig

def top_categories_bar(df, top_n=15):
    s = df['categories'].fillna("Unknown")
    # muchas filas pueden tener listas separadas por ','; contar cada categoría si es posible
    exploded = s.str.split(',').explode().str.strip()
    counts = exploded.value_counts().nlargest(top_n)
    fig = px.bar(x=counts.values, y=counts.index, orientation='h', title=f"Top {top_n} categorías")
    fig.update_layout(xaxis_title="Libros", yaxis_title="Categoría", height=400)
    return fig

import plotly.express as px

def plot_publication_years(df):
    fig = px.histogram(df, x='published_year', nbins=50,
                       title='Publicaciones por año',
                       color_discrete_sequence=['#6b4c3b'])
    fig.update_layout(plot_bgcolor='#f6f2e9', paper_bgcolor='#f6f2e9')
    return fig

def plot_average_rating_distribution(df):
    fig = px.histogram(df, x='average_rating', nbins=10,
                       title='Distribución de puntuaciones',
                       color_discrete_sequence=['#3e6b3e'])
    fig.update_layout(plot_bgcolor='#f6f2e9', paper_bgcolor='#f6f2e9')
    return fig
