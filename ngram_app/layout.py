# -*- coding: utf-8 -*-
"""
Layout components for the N-gram Dash application.
"""

import dash_bootstrap_components as dbc
from dash import dcc, html
import datetime

from .utils import (
    SCHEMES, LANGUAGES, MODES, CORPORA, 
    DEFAULT_SMOOTHING, DEFAULT_WORD, CURRENT_YEAR, DEFAULT_YEAR_RANGE
)

# ==========================================
# LAYOUT COMPONENTS
# ==========================================

def create_search_controls():
    return html.Div([
        # ✅ Move settings button to the left
        html.Div(
            dbc.Button(
                html.I(className="fas fa-bars"),  # Hamburger icon
                id="toggle_sidebar",
                n_clicks=0,
                color="secondary",
                outline=True,
                className="me-2 d-block"
            ),
            className="custom-flex-col width-10 mb-3 d-flex align-items-center justify-content-start"
        ),

        # ✅ Labels on top, inputs below
        html.Div([
            html.Label("Words:", className="form-label"),
            dbc.Input(
                id='words',
                type='text',
                value=DEFAULT_WORD,
                placeholder='Søk ord (f.eks. frihet, likhet)',
                debounce=True,
            )
        ], className="custom-flex-col width-35 mb-3"),

        html.Div([
            html.Label("Corpus:", className="form-label"),
            dbc.Select(
                id='korpus',
                options=CORPORA,
                value='avis',
            )
        ], className="custom-flex-col width-20 mb-3"),

        html.Div([
            html.Label("Lang:", className="form-label"),
            dbc.Select(
                id='lang',
                options=[{'label': l, 'value': l} for l in LANGUAGES],
                value='nob',
                disabled=True
            )
        ], className="custom-flex-col width-15 mb-3"),

        html.Div([
            html.Label("Mode:", className="form-label"),
            dbc.Select(
                id='mode',
                options=MODES,
                value='relative',
            )
        ], className="custom-flex-col width-20 mb-3"),

    ], className="custom-flex-row mb-4 align-items-center")




def create_chart_component():
    """
    Create the chart component.
    
    Returns:
        dbc.Card: Chart component
    """
    return dbc.Card([
        dbc.CardBody([
            dcc.Graph(
                id='ngram_chart', 
                style={'height': '70vh'}, 
                config={'scrollZoom': True},  # ✅ Allow zooming (useful)
                clickData=None  # ✅ Ensure click data is initialized
            ),

            # ✅ ADD THIS: Summary below the graph
            html.Div(id='content_summary', className="text-muted small mt-2"),

            # Click output text
            html.Div(id='graph_click_output', className="text-muted small mt-2"),

            # Search options dropdown (hidden initially)
            dbc.Collapse(
                dbc.Card([
                    dbc.CardBody([
                        html.P("Hva vil du søke etter?", className="fw-bold"),
                        dbc.Select(
                            id="search_option",
                            options=[
                                {"label": "Søk i dette året", "value": "year"},
                                {"label": "Søk i denne perioden", "value": "period"},
                                {"label": "Søk i hele arkivet", "value": "all"}
                            ],
                            placeholder="Velg søk...",
                        ),
                        dbc.Button("Utfør søk", id="search_button", color="primary", className="mt-2"),
                        html.Div(id="search_result", className="mt-3 text-muted")
                    ])
                ]),
                id="search_collapse",
                is_open=False  # Initially hidden
                
            )
        ])
    ])


def create_sidebar():
    """
    Create the settings sidebar.
    
    Returns:
        dbc.Offcanvas: Settings sidebar component
    """
    return dbc.Offcanvas(
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
def create_layout():
    """
    Create the main application layout.
    
    Returns:
        dbc.Container: Main application layout
    """
    return dbc.Container([
        html.Link(
            rel="stylesheet",
            href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css"
        ),
        dbc.Row([
            dbc.Col([
                html.H1("N-gram Viewer", className="my-4"),
                create_search_controls(),
                create_chart_component(),
                create_sidebar(),
                dcc.Store(id='data_store'),
                dcc.Download(id="download_excel")
            ])
        ])
    ], fluid=True, className="py-3")