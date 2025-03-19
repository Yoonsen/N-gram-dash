# -*- coding: utf-8 -*-
"""
Main application file for the N-gram Dash app.
"""

import dash
import dash_bootstrap_components as dbc
from dash import callback

from .layout import create_layout
from .callbacks import register_callbacks

def create_app():
    """
    Create and configure the Dash application.
    
    Returns:
        dash.Dash: Configured Dash application
    """
    # Initialize the app with external stylesheets
    app = dash.Dash(
        __name__, 
        title="N-gram", 
        external_stylesheets=[dbc.themes.FLATLY]
    )
    
    # Set the app layout
    app.layout = create_layout()
    
    # Register callbacks
    register_callbacks()
    
    return app

def main():
    """
    Main entry point for running the application.
    """
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=9050)

if __name__ == '__main__':
    main()