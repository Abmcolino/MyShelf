# src/model.py
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from src.etl import load_books

def build_content_model(df):
    """
    Construye la matriz de similitud TF-IDF a partir de los campos de texto combinados.
    """
    # columnas de texto que usaremos para TF-IDF
    text_cols = ['title', 'authors', 'categories', 'description', 'subtitle']
    
    # rellenar solo columnas de texto
    for col in text_cols:
        if col in df.columns:
            df[col] = df[col].fillna('')

    # combinar las columnas de texto
    combined_features = df[text_cols].agg(' '.join, axis=1)

    # TF-IDF + similitud coseno
    vectorizer = TfidfVectorizer(stop_words='english')
    feature_vectors = vectorizer.fit_transform(combined_features)
    similarity = cosine_similarity(feature_vectors, feature_vectors)

    return similarity, df

def recommend_content(df, isbn, top_n=10):
    """
    Recomendaciones content-based: devuelve un DataFrame con los top_n libros similares.
    """
    similarity, df = build_content_model(df)

    if isbn not in df['isbn13'].values:
        return pd.DataFrame()  # isbn no encontrado

    index_of_the_book = df[df['isbn13'] == isbn].index[0]
    similarity_score = list(enumerate(similarity[index_of_the_book]))
    sorted_similar_books = sorted(similarity_score, key=lambda x: x[1], reverse=True)[1:top_n+1]

    recs = df.iloc[[i[0] for i in sorted_similar_books]].copy()
    recs['similarity_score'] = [i[1] for i in sorted_similar_books]

    return recs

def top_recommended_books(recs_df, top_n=10):
    """
    Devuelve los libros más recomendados (por frecuencia de aparición en recomendaciones)
    """
    if recs_df.empty:
        return pd.DataFrame()
    
    top_books = recs_df['title'].value_counts().head(top_n).reset_index()
    top_books.columns = ['title', 'count']
    return top_books
