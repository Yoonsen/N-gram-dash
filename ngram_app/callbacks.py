# -*- coding: utf-8 -*-
"""
Callback functions for the N-gram Dash application.
"""

import dash
from dash import Input, Output, State, callback, dcc, html
import plotly.graph_objs as go
from io import StringIO
import pandas as pd
import datetime

from .utils import to_excel, get_ngram, process_chart_data

def register_callbacks():
    """
    Register all callbacks for the application.
    """
    
    # Toggle sidebar
    @callback(
        Output('sidebar', 'is_open'),
        Input('toggle_sidebar', 'n_clicks'),
        State('sidebar', 'is_open')
    )
    def toggle_sidebar(n_clicks, is_open):
        """
        Toggle the visibility of the sidebar.
        
        Args:
            n_clicks (int): Number of clicks on the toggle button
            is_open (bool): Current state of the sidebar
            
        Returns:
            bool: New state of the sidebar
        """
        return not is_open if n_clicks else is_open

    # Enable/disable lang based on korpus
    @callback(
        Output('lang', 'disabled'),
        Input('korpus', 'value')
    )
    def update_lang_disabled(korpus):
        """
        Enable/disable language dropdown based on corpus selection.
        
        Args:
            korpus (str): Selected corpus
            
        Returns:
            bool: True if language dropdown should be disabled
        """
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
        """
        Update the raw data store with n-gram data.
        
        Args:
            words (str): Comma-separated list of words to search
            korpus (str): Selected corpus
            lang (str): Selected language
            mode (str): Selected display mode
            years (list): Selected year range [start_year, end_year]
            
        Returns:
            str: JSON representation of the n-gram data
        """
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
        """
        Update the chart display, summary text, and handle downloads.
        
        Args:
            data_json (str): JSON data from data store
            mode (str): Selected display mode
            smooth (int): Smoothing value
            years (list): Selected year range
            theme (str): Selected chart theme
            alpha (float): Opacity value
            width (float): Line width value
            n_clicks (int): Number of clicks on download button
            words (str): Comma-separated list of words
            korpus (str): Selected corpus
            filnavn (str): Filename for download
            
        Returns:
            tuple: (figure, summary, download_data)
        """
        ctx = dash.callback_context
        if data_json is None:
            return go.Figure(), "Ingen data", None
        
        ngram = pd.read_json(StringIO(data_json))
        from_year, to_year = years
        start_date = pd.Timestamp(f"{from_year}-01-01").strftime('%Y%m%d')
        end_date = pd.Timestamp(f"{to_year}-12-31").strftime('%Y%m%d')
        mediatype = 'aviser' if korpus == 'avis' else 'bøker'

        # Process data based on selected mode
        chart = process_chart_data(ngram, mode, smooth)

        # Create traces for each column in the chart
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

        # Create layout
        layout = go.Layout(
            template=theme if theme is not None else 'plotly_white',
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