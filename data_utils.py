# data_utils.py
# Helper functions for data loading and OLAP execution

import pandas as pd
import streamlit as st
import traceback

@st.cache_data  # Cache so data loads only once
def load_data(filepath='data/Complete.csv'):
    """Load and cache the BedBath&Beyond dataset."""
    df = pd.read_csv(filepath, encoding='latin-1', low_memory=False)

    # Ensure price columns are numeric
    df['REG_PRICE'] = pd.to_numeric(df['REG_PRICE'], errors='coerce')
    df['SALE_PRICE'] = pd.to_numeric(df['SALE_PRICE'], errors='coerce')

    return df

def execute_olap_code(df, code_string):
    """
    Safely execute AI-generated pandas code.
    Returns (result_dataframe, error_message)
    """
    local_vars = {'df': df.copy(), 'pd': pd}
    try:
        exec(code_string, {}, local_vars)
        result = local_vars.get('result', None)
        if result is None:
            return None, 'Code ran but did not produce a variable named result'
        if not isinstance(result, pd.DataFrame):
            result = pd.DataFrame({'Result': [str(result)]})
        return result, None
    except Exception as e:
        return None, f'Error: {str(e)}'

def get_dataset_summary(df):
    """Return a dict of key statistics about the dataset."""
    return {
        'total_products': len(df),
        'brands': df['BRAND'].nunique(),
        'categories': df['CATEGORY'].nunique(),
        'in_stock': (df['AVAILABILITY'] == 'IN STOCK').sum(),
        'on_sale': df['SALE_PRICE'].notna().sum(),
        'avg_price': round(df['REG_PRICE'].mean(), 2),
    }