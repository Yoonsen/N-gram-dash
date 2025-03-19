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
    """
    Create the search controls for the application.
    
    Returns:
        dbc.Row: Search controls component
    """
    return dbc.Row([
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

def create_chart_component():
    """
    Create the chart component.
    
    Returns:
        dbc.Card: Chart component
    """
    return dbc.Card([
        dbc.CardBody([
            dcc.Graph(id='ngram_chart', style={'height': '70vh'}),
            html.Div(id='content_summary', className="text-muted small mt-2")
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