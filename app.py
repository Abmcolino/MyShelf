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

LOGO_PATH = "myshelf/logo.png"

# ---------------------------------------------------------
# ⭐ LAYOUT PRINCIPAL
# ---------------------------------------------------------
app.layout = dbc.Container([

    # LOGO CENTRADO
    dbc.Row(
        dbc.Col(
            html.Img(
                src=LOGO_PATH,
                style={'max-height': '80px', 'cursor': 'pointer'},
                id='logo-btn'
            ),
            width='auto'
        ),
        justify='center',
        className='my-3'
    ),

    # MENÚ SUPERIOR: SOLO "INICIO"
    dbc.Row(
        dbc.Col(
            dbc.Nav(
                [
                    dbc.NavItem(
                        dbc.NavLink(
                            "Inicio",
                            href="/",
                            active="exact",
                            className="px-3 py-1",
                            style={
                                "fontSize": "0.9rem",
                                "backgroundColor": "#ffffff",
                                "borderRadius": "12px",
                                "boxShadow": "0 2px 5px rgba(0,0,0,0.1)",
                                "display": "inline-block",
                                "width": "120px",
                                "textAlign": "center"
                            }
                        )
                    )
                ],
                pills=False,
                justified=False,
                className="mb-2",
                style={"display": "flex", "justifyContent": "center"}
            )
        )
    ),

    # MENÚ INFERIOR
    dbc.Row(
        dbc.Col(
            dbc.Nav(
                [
                    dbc.NavItem(dbc.NavLink("Explorador", href="/explore", active="exact")),
                    dbc.NavItem(dbc.NavLink("Recomendador", href="/recommend", active="exact")),
                    dbc.NavItem(dbc.NavLink("Editar Base de Datos", href="/edit", active="exact")),
                    dbc.NavItem(dbc.NavLink("Lecturas", href="/readings", active="exact")),
                    dbc.NavItem(dbc.NavLink("Añadir libros", href="/add-books", active="exact")),
                    dbc.NavItem(dbc.NavLink("Reseñas", href="/resenas", active="exact")),  # SIN ACENTO
                ],
                pills=True,
                justified=True,
                className='mb-4 shadow-sm rounded-pill custom-nav'
            ),
            width=12
        )
    ),

    # CONTENIDO DE LA PÁGINA
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content', style={'minHeight': '600px'})

], fluid=True, style={'backgroundColor':'#f4f1e0', 'fontFamily':'Georgia, serif', 'color':'#3b2f2f'})


# ---------------------------------------------------------
# CALLBACK: CAMBIO DE PÁGINAS (con captura de errores y traceback visual)
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
        elif pathname == "/resenas":  # SIN ACENTO
            return reseñas_layout()
        else:
            return home_layout()

    except Exception as e:
        # Si algo falla al renderizar una página, devolvemos un panel con el traceback
        tb = traceback.format_exc()
        return dbc.Container([
            dbc.Alert("Se ha producido un error al cargar la página. Aquí tienes el traceback:", color="danger"),
            html.Pre(tb, style={'whiteSpace':'pre-wrap', 'overflowX':'auto', 'maxHeight':'400px'}),
            html.Hr(),
            html.P("Comprueba la consola donde ejecutas python para ver la traza completa.")
        ], className='mt-3')


# ---------------------------------------------------------
# LOGO → HOME
# ---------------------------------------------------------
@app.callback(
    dash.Output('url', 'pathname'),
    dash.Input('logo-btn', 'n_clicks'),
    prevent_initial_call=True
)
def go_home(n):
    return "/"


# ---------------------------------------------------------
# REGISTRO DE CALLBACKS
# ---------------------------------------------------------
# Registra todos los callbacks de cada página
register_edit_callbacks(app)
register_readings_callbacks(app)
register_recommend_callbacks(app)
register_add_books_callbacks(app)
register_reseñas_callbacks(app)
register_explore_callbacks(app)  # debe coincidir con la definición en src/pages/explore.py

# ---------------------------------------------------------
# EJECUCIÓN
# ---------------------------------------------------------
if __name__ == "__main__":
    app.run(debug=True, port=8050)
