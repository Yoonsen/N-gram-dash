import dash
from dash import Input, Output, State, callback, dcc, html
import plotly.graph_objs as go
from io import StringIO
import pandas as pd
import datetime
from .utils import to_excel, get_ngram, process_chart_data

# ✅ Sidebar toggle
@callback(
    Output('sidebar', 'is_open'),
    Input('toggle_sidebar', 'n_clicks'),
    State('sidebar', 'is_open')
)
def toggle_sidebar(n_clicks, is_open):
    return not is_open if n_clicks else is_open

# ✅ Enable/disable language selection
@callback(
    Output('lang', 'disabled'),
    Input('korpus', 'value')
)
def update_lang_disabled(korpus):
    return korpus == 'avis'

# ✅ Update data store
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

# ✅ Update chart
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

    # Process data based on selected mode
    chart = process_chart_data(ngram, mode, smooth)

    # Create traces for each column in the chart
    traces = [
        go.Scatter(
            x=chart.index,
            y=chart[col],
            mode='lines',
            name=col,
            opacity=alpha if alpha is not None else 0.9,
            line=dict(width=width if width is not None else 3.0),
            hovertemplate=f"{col}<br>Date: %{{x}}<br>Freq: %{{y}}"
        ) for col in chart.columns
    ]

    # Create layout
    fig = go.Figure(
        data=traces,
        layout=go.Layout(
            template=theme if theme is not None else 'plotly_white',
            xaxis_title="Dato",
            yaxis_title="Frekvens",
            hovermode="x unified",
            margin=dict(l=40, r=40, t=10, b=40)
        )
    )

    # Add summary
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

@callback(
    [Output('graph_click_output', 'children'),
     Output('search_collapse', 'is_open')],
    Input('ngram_chart', 'clickData')
)
def handle_graph_click(clickData):
    print(f"DEBUG: ClickData - {clickData}")  # ✅ Print in logs

    if not clickData:
        return "Klikk på et datapunkt for mer informasjon.", False

    point = clickData['points'][0]
    x_value = point.get('x', 'Ukjent X')
    y_value = point.get('y', 'Ukjent Y')
    series = point.get('curveNumber', 'Ukjent serie')

    message = f"Valgt datapunkt: {x_value}, Frekvens: {y_value} (Serie {series})"
    
    return message, True


# ✅ Handle search execution
@callback(
    Output('search_result', 'children'),
    Input('search_button', 'n_clicks'),
    State('search_option', 'value'),
    State('ngram_chart', 'clickData')
)
def execute_search(n_clicks, search_option, clickData):
    if not n_clicks or not clickData or not search_option:
        return ""

    point = clickData['points'][0]
    year = point['x']
    term = point.get('text') if 'text' in point else "Ukjent"

    if search_option == "year":
        return f"Søker etter '{term}' i året {year}..."
    elif search_option == "period":
        return f"Søker etter '{term}' i perioden {year-5} til {year+5}..."
    elif search_option == "all":
        return f"Søker etter '{term}' i hele arkivet..."
    
    return "Ukjent søkevalg."
