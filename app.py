# -*- coding: utf-8 -*-

import dash
import dash_bootstrap_components as dbc
from dash import dcc, html, Input, Output, State
import pandas as pd
from io import BytesIO, StringIO
import datetime
import plotly.graph_objs as go
import base64
import dhlab.ngram as ng
from urllib.parse import urlencode

# Constants
schemes = ['plotly', 'plotly_white', 'plotly_dark']

# Utility functions
def to_excel(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=True, sheet_name='Sheet1')
    return output.getvalue()

def get_ngram(words=None, from_year=None, to_year=None, doctype=None, lang='nob', mode='relative'):
    if 'bok' in doctype:
        corpus = 'bok'
    else:
        corpus = 'avis'
    a = ng.nb_ngram.nb_ngram(' ,'.join(words), corpus=corpus, smooth=1, years=(from_year, to_year), mode=mode, lang=lang)
    a.index = pd.to_datetime(a.index, format='%Y')
    return a

def make_nb_query(name, mediatype, start_date, end_date):
    return f"https://www.nb.no/search?mediatype={mediatype}&" + urlencode({'q': f'"{name}"', 'fromDate': f"{start_date}", 'toDate': f"{end_date}"})

# Initialize Dash app
app = dash.Dash(__name__, title="N-gram", external_stylesheets=[dbc.themes.FLATLY])

# Layout
app.layout = html.Div([
    # Main content row
    dbc.Row([
        dbc.Col(
            dcc.Input(
                id='words', 
                type='text', 
                value='frihet', 
                placeholder='Søk ord (f.eks. frihet, likhet)', 
                debounce=True, 
                className="mb-3 mt-3",
                style={'border': '1px solid #ccc', 'borderRadius': '4px', 'padding': '6px 12px'}
            ),
            width=3
        ),
        dbc.Col(
            dcc.Dropdown(
                id='korpus', 
                options=[{'label': 'Avis', 'value': 'avis'}, {'label': 'Bok', 'value': 'bok'}], 
                value='avis', 
                placeholder="Select corpus",
                className="mb-3 mt-3",
                style={'border': '1px solid #ccc', 'borderRadius': '4px'}
            ),
            width=2
        ),
        dbc.Col(
            dcc.Dropdown(
                id='lang', 
                options=[{'label': l, 'value': l} for l in ['nob', 'nno', 'sme', 'fkv']], 
                value='nob', 
                placeholder="Select language",
                className="mb-3 mt-3",
                style={'border': '1px solid #ccc', 'borderRadius': '4px'},
                disabled=True
            ),
            width=2
        ),
        dbc.Col(
            dcc.Dropdown(
                id='mode', 
                options=[
                    {'label': 'Relativ', 'value': 'relative'},
                    {'label': 'Absolutt', 'value': 'absolute'},
                    {'label': 'Kumulativ', 'value': 'cumulative'},
                    {'label': 'Kohort', 'value': 'cohort'}
                ], 
                value='relative', 
                placeholder="Select frequency type",
                className="mb-3 mt-3",
                style={'border': '1px solid #ccc', 'borderRadius': '4px'}
            ),
            width=2
        ),
        dbc.Col(
            dbc.Button(
                "⚙️ Settings",  # Simple gear icon with text, no green
                id="toggle_sidebar",
                n_clicks=0,
                color="secondary",  # Gray, neutral tone
                outline=True,  # Removes solid background
                style={'fontSize': '16px', 'padding': '5px 10px', 'zIndex': '1001'}
            ),
            width=1,
            className="text-end"
        )
    ], className="mb-4", style={'position': 'relative', 'zIndex': '1000'}),

    dcc.Graph(id='ngram_chart', style={'height': '70vh'}),
    html.Div(id='content_summary', className="text-muted small mb-4 mt-2", style={'marginLeft': '20px', 'marginRight': '20px'}),

    # Sidebar
    dbc.Collapse(
        dbc.Card([
            dbc.CardBody([
                html.H4("Settings", className="card-title"),
                dbc.Label("Glatting"),
                dcc.Slider(id='smooth', min=1, max=10, step=1, value=4, marks={1: '1', 10: '10'}, className="mb-3"),
                dbc.Label("Periode"),
                dcc.RangeSlider(
                    id='years', 
                    min=1810, 
                    max=datetime.date.today().year, 
                    step=1, 
                    value=[1954, datetime.date.today().year], 
                    marks={1810: '1810', datetime.date.today().year: str(datetime.date.today().year)}, 
                    className="mb-3"
                ),
                dbc.Label("Fargetema"),
                dcc.Dropdown(id='theme', options=[{'label': t, 'value': t} for t in schemes], value='plotly', className="form-control mb-3"),
                dbc.Label("Gjennomsiktighet"),
                dcc.Input(id='alpha', type='number', value=0.9, min=0.1, max=1.0, step=0.1, className="form-control mb-3"),
                dbc.Label("Linjetykkelse"),
                dcc.Input(id='width', type='number', value=3.0, min=0.5, max=30.0, step=0.5, className="form-control mb-3"),
                dbc.Label("Last ned"),
                dcc.Input(id='filnavn', type='text', value=f"ngram_{datetime.date.today().strftime('%Y%m%d')}_{datetime.date.today().strftime('%Y%m%d')}.xlsx", className="form-control mb-3"),
                dbc.Button("Last ned", id="btn_download", n_clicks=0, color="primary", className="w-100"),
                dcc.Download(id="download_excel")
            ])
        ], style={'width': '300px'}),
        id="sidebar",
        is_open=False,
        className="position-fixed",
        style={'top': '50px', 'left': '10px', 'zIndex': '998'}
    ),
    dcc.Store(id='data_store')
], className="container-fluid", style={'padding': '20px'})

# Toggle sidebar
@app.callback(
    Output('sidebar', 'is_open'),
    Input('toggle_sidebar', 'n_clicks'),
    State('sidebar', 'is_open')
)
def toggle_sidebar(n_clicks, is_open):
    return not is_open if n_clicks else is_open

# Enable/disable lang based on korpus
@app.callback(
    Output('lang', 'disabled'),
    Input('korpus', 'value')
)
def update_lang_disabled(korpus):
    return korpus == 'avis'

# Update raw data store
@app.callback(
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
@app.callback(
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
        height=500,
        xaxis_title="Dato",
        yaxis_title="Frekvens",
        hovermode="x unified"
    )
    fig = go.Figure(data=traces, layout=layout)

    summary = f"Søk: {words} | Korpus: {korpus.capitalize()} | Periode: {from_year} til {to_year}"
    if n_clicks > 0:
        excel_data = to_excel(chart)
        return fig, summary, dcc.send_bytes(excel_data, filnavn)
    return fig, summary, None

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=9050)