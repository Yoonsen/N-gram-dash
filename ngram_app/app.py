# -*- coding: utf-8 -*-

import dash
import dash_bootstrap_components as dbc
from dash import dcc, html, Input, Output, State, callback
import pandas as pd
from io import BytesIO, StringIO
import datetime
import plotly.graph_objs as go
import base64
import dhlab.ngram as ng
from urllib.parse import urlencode

# ==========================================
# CONFIGURATION
# ==========================================

# Constants and settings
SCHEMES = [
    'plotly_white', 
    'plotly', 
    'plotly_dark', 
    'ggplot2', 
    'seaborn', 
    'simple_white'
]
LANGUAGES = ['nob', 'nno', 'sme', 'fkv']
MODES = [
    {'label': 'Relativ', 'value': 'relative'},
    {'label': 'Absolutt', 'value': 'absolute'},
    {'label': 'Kumulativ', 'value': 'cumulative'},
    {'label': 'Kohort', 'value': 'cohort'}
]
CORPORA = [
    {'label': 'Avis', 'value': 'avis'}, 
    {'label': 'Bok', 'value': 'bok'}
]
DEFAULT_SMOOTHING = 4
DEFAULT_WORD = 'frihet'
CURRENT_YEAR = datetime.date.today().year
DEFAULT_YEAR_RANGE = [1954, CURRENT_YEAR]

# ==========================================
# UTILITY FUNCTIONS
# ==========================================

def to_excel(df):
    """Convert a DataFrame to Excel bytes"""
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=True, sheet_name='Sheet1')
    return output.getvalue()

def get_ngram(words=None, from_year=None, to_year=None, doctype=None, lang='nob', mode='relative'):
    """Fetch n-gram data from the dhlab API"""
    corpus = 'bok' if 'bok' in doctype else 'avis'
    a = ng.nb_ngram.nb_ngram(' ,'.join(words), corpus=corpus, smooth=1, years=(from_year, to_year), mode=mode, lang=lang)
    a.index = pd.to_datetime(a.index, format='%Y')
    return a

def make_nb_query(name, mediatype, start_date, end_date):
    """Create a National Library search query URL"""
    return f"https://www.nb.no/search?mediatype={mediatype}&" + urlencode({'q': f'"{name}"', 'fromDate': f"{start_date}", 'toDate': f"{end_date}"})

# ==========================================
# APP INITIALIZATION
# ==========================================

app = dash.Dash(
    __name__, 
    title="N-gram", 
    external_stylesheets=[dbc.themes.FLATLY]
)

# ==========================================
# LAYOUT COMPONENTS
# ==========================================

# Single row for all controls
search_controls = dbc.Row([
    # Word input - larger width for main search
    dbc.Col(
        dbc.InputGroup([
            dbc.InputGroupText("Words:"),
            dbc.Input(
                id='words', 
                type='text', 
                value=DEFAULT_WORD, 
                placeholder='Søk ord (f.eks. frihet, likhet)', 
                debounce=True,
            )
        ]),
        width=4, className="mb-3"
    ),
    
    # Corpus dropdown - smaller width
    dbc.Col(
        dbc.InputGroup([
            dbc.InputGroupText("Corpus:"),
            dbc.Select(
                id='korpus', 
                options=CORPORA, 
                value='avis',
            )
        ]),
        width=2, className="mb-3"
    ),
    
    # Language dropdown - smaller width
    dbc.Col(
        dbc.InputGroup([
            dbc.InputGroupText("Lang:"),
            dbc.Select(
                id='lang', 
                options=[{'label': l, 'value': l} for l in LANGUAGES], 
                value='nob',
                disabled=True
            )
        ]),
        width=2, className="mb-3"
    ),
    
    # Mode selector - smaller width
    dbc.Col(
        dbc.InputGroup([
            dbc.InputGroupText("Mode:"),
            dbc.Select(
                id='mode', 
                options=MODES, 
                value='relative',
            )
        ]),
        width=2, className="mb-3"
    ),
    
    # Settings button - smallest width
    dbc.Col(
        dbc.Button(
            html.I(className="fas fa-bars"), # Hamburger icon
            id="toggle_sidebar",
            n_clicks=0,
            color="secondary",
            outline=True,
            className="ms-auto d-block"
        ),
        width=1, className="mb-3 d-flex align-items-center justify-content-end"
    )
], className="mb-4 g-2 align-items-center")

# Chart component
chart_component = dbc.Card([
    dbc.CardBody([
        dcc.Graph(id='ngram_chart', style={'height': '70vh'}),
        html.Div(id='content_summary', className="text-muted small mt-2")
    ])
])

# Settings Sidebar
sidebar = dbc.Offcanvas(
    [
        html.H4("Settings", className="mb-4"),
        
        # Smoothing
        dbc.Label("Glatting", className="mb-1"),
        dcc.Slider(
            id='smooth', 
            min=1, 
            max=10, 
            step=1, 
            value=DEFAULT_SMOOTHING, 
            marks={1: '1', 5: '5', 10: '10'}, 
            className="mb-4"
        ),
        
        # Year range
        dbc.Label("Periode", className="mb-1"),
        dcc.RangeSlider(
            id='years', 
            min=1810, 
            max=CURRENT_YEAR, 
            step=1, 
            value=DEFAULT_YEAR_RANGE, 
            marks={
                1810: '1810', 
                1900: '1900', 
                2000: '2000',
                CURRENT_YEAR: str(CURRENT_YEAR)
            }, 
            className="mb-4"
        ),
        
        # Theme
        dbc.Label("Fargetema", className="mb-1"),
        dbc.Select(
            id='theme', 
            options=[{'label': t, 'value': t} for t in SCHEMES], 
            value='plotly_white', 
            className="mb-4"
        ),
        
        # Opacity
        dbc.Label("Gjennomsiktighet", className="mb-1"),
        dbc.Input(
            id='alpha', 
            type='number', 
            value=0.9, 
            min=0.1, 
            max=1.0, 
            step=0.1, 
            className="mb-4"
        ),
        
        # Line width
        dbc.Label("Linjetykkelse", className="mb-1"),
        dbc.Input(
            id='width', 
            type='number', 
            value=3.0, 
            min=0.5, 
            max=30.0, 
            step=0.5, 
            className="mb-4"
        ),
        
        # Download
        dbc.Label("Last ned", className="mb-1"),
        dbc.Input(
            id='filnavn', 
            type='text', 
            value=f"ngram_{datetime.date.today().strftime('%Y%m%d')}.xlsx", 
            className="mb-2"
        ),
        dbc.Button(
            "Last ned", 
            id="btn_download", 
            color="primary", 
            className="w-100 mt-2"
        )
    ],
    id="sidebar",
    title="Settings",
    is_open=False,
    placement="end"
)

# ==========================================
# MAIN LAYOUT
# ==========================================

app.layout = dbc.Container([
    html.Link(
        rel="stylesheet",
        href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css"
    ),
    dbc.Row([
        dbc.Col([
            html.H1("N-gram Viewer", className="my-4"),
            search_controls,
            chart_component,
            sidebar,
            dcc.Store(id='data_store'),
            dcc.Download(id="download_excel")
        ])
    ])
], fluid=True, className="py-3")

# ==========================================
# CALLBACKS
# ==========================================

# Toggle sidebar
@callback(
    Output('sidebar', 'is_open'),
    Input('toggle_sidebar', 'n_clicks'),
    State('sidebar', 'is_open')
)
def toggle_sidebar(n_clicks, is_open):
    return not is_open if n_clicks else is_open

# Enable/disable lang based on korpus
@callback(
    Output('lang', 'disabled'),
    Input('korpus', 'value')
)
def update_lang_disabled(korpus):
    return korpus == 'avis'

# Update raw data store
@callback(
    Output('data_store', 'data'),
    [Input('words', 'value'),
     Input('korpus', 'value'),
     Input('lang', 'value'),
     Input('mode', 'value'),
     Input('years', 'value')]
)
def update_data(words, korpus, lang, mode, years):
    if not words:
        return None
    words = [x.strip() for x in words.split(',')]
    from_year, to_year = years
    mode_map = {'relative': 'relative', 'absolute': 'absolutt', 'cumulative': 'absolutt', 'cohort': 'absolutt'}
    ngram = get_ngram(words=words, from_year=from_year, to_year=to_year, doctype=korpus, lang=lang if korpus != 'avis' else 'nob', mode=mode_map[mode])
    return ngram.to_json(date_format='iso')

# Update chart, summary, and download
@callback(
    [Output('ngram_chart', 'figure'),
     Output('content_summary', 'children'),
     Output('download_excel', 'data')],
    [Input('data_store', 'data'),
     Input('mode', 'value'),
     Input('smooth', 'value'),
     Input('years', 'value'),
     Input('theme', 'value'),
     Input('alpha', 'value'),
     Input('width', 'value'),
     Input('btn_download', 'n_clicks')],
    [State('words', 'value'),
     State('korpus', 'value'),
     State('filnavn', 'value')]
)
def update_chart(data_json, mode, smooth, years, theme, alpha, width, n_clicks, words, korpus, filnavn):
    ctx = dash.callback_context
    if data_json is None:
        return go.Figure(), "Ingen data", None
    
    ngram = pd.read_json(StringIO(data_json))
    from_year, to_year = years
    start_date = pd.Timestamp(f"{from_year}-01-01").strftime('%Y%m%d')
    end_date = pd.Timestamp(f"{to_year}-12-31").strftime('%Y%m%d')
    mediatype = 'aviser' if korpus == 'avis' else 'bøker'

    if mode == 'cumulative':
        chart = ngram.cumsum()
    elif mode == 'cohort':
        chart = (ngram.transpose() / ngram.sum(axis=1)).transpose().rolling(window=smooth, win_type='triang').mean()
    else:
        chart = ngram.rolling(window=smooth, win_type='triang').mean()

    traces = []
    for col in chart.columns:
        traces.append(go.Scatter(
            x=chart.index,
            y=chart[col],
            mode='lines',
            name=col,
            opacity=alpha if alpha is not None else 0.9,
            line=dict(width=width if width is not None else 3.0),
            hovertemplate=f"{col}<br>Date: %{{x}}<br>Freq: %{{y}}"
        ))

    layout = go.Layout(
        template=theme if theme is not None else 'plotly',
        xaxis_title="Dato",
        yaxis_title="Frekvens",
        hovermode="x unified",
        margin=dict(l=40, r=40, t=10, b=40)
    )
    fig = go.Figure(data=traces, layout=layout)

    # Add data summary below chart
    summary = html.Div([
        html.Span(f"Søk: ", className="fw-bold"),
        html.Span(f"{words}"),
        html.Span(f" | Korpus: ", className="fw-bold ms-2"),
        html.Span(f"{korpus.capitalize()}"),
        html.Span(f" | Periode: ", className="fw-bold ms-2"),
        html.Span(f"{from_year} til {to_year}")
    ])

    # Handle download button click
    triggered = ctx.triggered[0]['prop_id'].split('.')[0] if ctx.triggered else None
    if triggered == 'btn_download':
        excel_data = to_excel(chart)
        return fig, summary, dcc.send_bytes(excel_data, filnavn)
    
    return fig, summary, None

# ==========================================
# RUN SERVER
# ==========================================

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=9050)