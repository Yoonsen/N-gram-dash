import os
import dash
import dash_bootstrap_components as dbc
from flask import Flask

from .layout import create_layout
from .callbacks import *  # ✅ Import all callbacks

import logging

logging.getLogger("werkzeug").setLevel(logging.WARNING)
logging.getLogger("dash").setLevel(logging.WARNING)

def create_app():
    """
    Create and configure the Dash application.
    Returns:
        tuple: (dash.Dash app, Flask server)
    """
    # Create Flask server
    server = Flask(__name__)

    # Determine if running in Cloud Run (production)
    is_production = os.getenv('ENVIRONMENT', 'development') == 'production'
    app_name = "nb-ngram"

    # Set correct path prefixes based on environment
    if is_production:
        requests_prefix = f"/run/{app_name}/"  # ✅ Cloud Run prefix
        routes_prefix = f"/{app_name}/"
    else:
        requests_prefix = "/"  # ✅ Local doesn't need this
        routes_prefix = "/"

    # Initialize Dash with correct prefixes
    app = dash.Dash(
        __name__,
        server=server,
        routes_pathname_prefix=routes_prefix,
        requests_pathname_prefix=requests_prefix,
        external_stylesheets=[
            dbc.themes.FLATLY,
            "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css"
        ],
        suppress_callback_exceptions=True
    )

    # Set the app layout
    app.layout = create_layout()

    return app, server

# Create app and server
app, server = create_app()

if __name__ == '__main__':
    server.run(debug=False, host='0.0.0.0', port=9050)
