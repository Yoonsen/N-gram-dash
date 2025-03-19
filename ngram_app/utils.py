# -*- coding: utf-8 -*-
"""
Utility functions for the N-gram Dash application.
"""

import pandas as pd
from io import BytesIO, StringIO
import datetime
import dhlab.ngram as ng
from urllib.parse import urlencode

# ==========================================
# CONSTANTS
# ==========================================

# Constants and settings
SCHEMES = ['plotly_white', 'plotly', 'plotly_dark', 'ggplot2', 'seaborn']
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
# DATA PROCESSING FUNCTIONS
# ==========================================

def to_excel(df):
    """
    Convert a DataFrame to Excel bytes.
    
    Args:
        df (pandas.DataFrame): DataFrame to convert to Excel
        
    Returns:
        bytes: Excel file content as bytes
    """
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=True, sheet_name='Sheet1')
    return output.getvalue()

def get_ngram(words=None, from_year=None, to_year=None, doctype=None, lang='nob', mode='relative'):
    """
    Fetch n-gram data from the dhlab API.
    
    Args:
        words (list): List of words to search for
        from_year (int): Start year for search
        to_year (int): End year for search
        doctype (str): Document type to search ('avis' or 'bok')
        lang (str): Language code to search
        mode (str): Mode for frequency calculation
        
    Returns:
        pandas.DataFrame: DataFrame with n-gram frequencies
    """
    corpus = 'bok' if 'bok' in doctype else 'avis'
    a = ng.nb_ngram.nb_ngram(' ,'.join(words), corpus=corpus, smooth=1, years=(from_year, to_year), mode=mode, lang=lang)
    a.index = pd.to_datetime(a.index, format='%Y')
    return a

def make_nb_query(name, mediatype, start_date, end_date):
    """
    Create a National Library search query URL.
    
    Args:
        name (str): Search term
        mediatype (str): Media type to search
        start_date (str): Start date in format YYYYMMDD
        end_date (str): End date in format YYYYMMDD
        
    Returns:
        str: URL for the search query
    """
    return f"https://www.nb.no/search?mediatype={mediatype}&" + urlencode({'q': f'"{name}"', 'fromDate': f"{start_date}", 'toDate': f"{end_date}"})

def process_chart_data(ngram, mode, smooth):
    """
    Process raw n-gram data into chart data based on selected mode.
    
    Args:
        ngram (pandas.DataFrame): Raw n-gram data
        mode (str): Display mode ('relative', 'absolute', 'cumulative', 'cohort')
        smooth (int): Smoothing window size
        
    Returns:
        pandas.DataFrame: Processed data ready for chart display
    """
    if mode == 'cumulative':
        chart = ngram.cumsum()
    elif mode == 'cohort':
        chart = (ngram.transpose() / ngram.sum(axis=1)).transpose().rolling(window=smooth, win_type='triang').mean()
    else:
        chart = ngram.rolling(window=smooth, win_type='triang').mean()
    
    return chart