# app.py
import dash
from dash import html, dcc
import dash_bootstrap_components as dbc
import traceback
import os

# Importar layouts y callbacks de cada página
from src.pages.edit import edit_form_layout, register_edit_callbacks
from src.pages.readings import readings_layout, register_readings_callbacks
from src.pages.explore import explore_layout, register_explore_callbacks
from src.pages.recommend import recommend_layout, register_callbacks as register_recommend_callbacks
from src.pages.addbooks import add_books_layout, register_add_books_callbacks
from src.pages.home import home_layout
from src.pages.resenas import reseñas_layout, register_reseñas_callbacks

# ---- Crear app ----
app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    suppress_callback_exceptions=True
)
server = app.server

# ---------------------------------------------------------
# Layout principal con menú
# ---------------------------------------------------------
app.layout = dbc.Container([
    # URL
    dcc.Location(id='url', refresh=False),

    # Menú superior
    dbc.Row(
        dbc.Col(
            dbc.Nav(
                [dbc.NavItem(dbc.NavLink("Inicio", href="/", active="exact"))],
                pills=False,
                justified=False,
                className="mb-2",
                style={"display": "flex", "justifyContent": "center"}
            )
        )
    ),

    # Menú inferior
    dbc.Row(
        dbc.Col(
            dbc.Nav(
                [
                    dbc.NavItem(dbc.NavLink("Explorador", href="/explore", active="exact")),
                    dbc.NavItem(dbc.NavLink("Recomendador", href="/recommend", active="exact")),
                    dbc.NavItem(dbc.NavLink("Editar Base de Datos", href="/edit", active="exact")),
                    dbc.NavItem(dbc.NavLink("Lecturas", href="/readings", active="exact")),
                    dbc.NavItem(dbc.NavLink("Añadir libros", href="/add-books", active="exact")),
                    dbc.NavItem(dbc.NavLink("Reseñas", href="/resenas", active="exact")),
                ],
                pills=True,
                justified=True,
                className='mb-4 shadow-sm rounded-pill custom-nav'
            ),
            width=12
        )
    ),

    # Contenido dinámico
    html.Div(id='page-content', style={'minHeight': '600px'})
], fluid=True, style={'backgroundColor':'#f4f1e0', 'fontFamily':'Georgia, serif', 'color':'#3b2f2f'})

# ---------------------------------------------------------
# Callback de navegación de páginas
# ---------------------------------------------------------
@app.callback(
    dash.Output('page-content', 'children'),
    dash.Input('url', 'pathname')
)
def display_page(pathname):
    try:
        if pathname == "/explore":
            return explore_layout()
        elif pathname == "/edit":
            return edit_form_layout()
        elif pathname == "/readings":
            return readings_layout()
        elif pathname == "/recommend":
            return recommend_layout()
        elif pathname == "/add-books":
            return add_books_layout()
        elif pathname == "/resenas":
            return reseñas_layout()
        else:
            return home_layout()
    except Exception:
        tb = traceback.format_exc()
        return dbc.Container([
            dbc.Alert("Se ha producido un error al cargar la página.", color="danger"),
            html.Pre(tb, style={'whiteSpace':'pre-wrap', 'overflowX':'auto', 'maxHeight':'400px'})
        ], className='mt-3')

# ---------------------------------------------------------
# Registro de callbacks de cada página
# ---------------------------------------------------------
register_edit_callbacks(app)
register_readings_callbacks(app)
register_recommend_callbacks(app)
register_add_books_callbacks(app)
register_reseñas_callbacks(app)
register_explore_callbacks(app)

# ---------------------------------------------------------
# Ejecución local
# ---------------------------------------------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8050))
    app.run(debug=True, host="0.0.0.0", port=port)
