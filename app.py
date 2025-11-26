# app.py
import dash
from dash import html, dcc
import dash_bootstrap_components as dbc
import traceback

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
# ⭐ LAYOUT PRINCIPAL
# ---------------------------------------------------------
# Layout base: home_layout como fallback para Render
app.layout = dbc.Container([
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content', children=home_layout())
], fluid=True)

# ---------------------------------------------------------
# CALLBACK: CAMBIO DE PÁGINAS
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
    except Exception as e:
        tb = traceback.format_exc()
        return dbc.Container([
            dbc.Alert("Se ha producido un error al cargar la página. Aquí tienes el traceback:", color="danger"),
            html.Pre(tb, style={'whiteSpace':'pre-wrap', 'overflowX':'auto', 'maxHeight':'400px'}),
            html.Hr(),
            html.P("Comprueba la consola donde ejecutas python para ver la traza completa.")
        ], className='mt-3')

# ---------------------------------------------------------
# REGISTRO DE CALLBACKS
# ---------------------------------------------------------
register_edit_callbacks(app)
register_readings_callbacks(app)
register_recommend_callbacks(app)
register_add_books_callbacks(app)
register_reseñas_callbacks(app)
register_explore_callbacks(app)

# ---------------------------------------------------------
# EJECUCIÓN LOCAL (solo para desarrollo)
# ---------------------------------------------------------
if __name__ == "__main__":
    app.run(debug=True)
