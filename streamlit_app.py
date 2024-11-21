import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.express as px
import plotly.graph_objs as go
import numpy as np

# Configuration of exchanges and asset types
EXCHANGES = {
    'US': {
        'stocks': ['SPY', 'QQQ', 'DIA'],
        'indices': ['^GSPC', '^DJI', '^IXIC'],
        'etfs': ['VTI', 'VEA', 'VWO']
    },
    'India': {
        'stocks': ['INFY.NS', 'TCS.NS', 'RELIANCE.NS'],
        'indices': ['^NSEI', '^BSESN'],
        'etfs': ['NIFTYBEES.NS', 'CPSEETF.NS']
    },
    'Europe': {
        'stocks': ['SAP.DE', 'NESN.SW', 'ABI.BR'],
        'indices': ['^STOXX50E', '^N100'],
        'etfs': ['EZU', 'VGK']
    }
}

def fetch_historical_data(ticker, start_date, end_date):
    """Fetch historical data for a given ticker."""
    try:
        data = yf.download(ticker, start=start_date, end=end_date)
        return data['Adj Close']
    except Exception as e:
        st.error(f"Error fetching data for {ticker}: {e}")
        return None

def calculate_correlation(series1, series2):
    """Calculate correlation between two price series."""
    merged = pd.concat([series1, series2], axis=1).dropna()
    return merged.corr().iloc[0, 1]

def normalize_data(series):
    """Normalize data to percentage change from start."""
    return series / series.iloc[0] * 100 - 100

def plot_performance_comparison(data1, data2, label1, label2):
    """Create a Plotly line chart comparing two asset performances."""
    fig = go.Figure()
    
    # Add first asset performance
    fig.add_trace(go.Scatter(
        x=data1.index, 
        y=data1, 
        mode='lines', 
        name=label1
    ))
    
    # Add second asset performance
    fig.add_trace(go.Scatter(
        x=data2.index, 
        y=data2, 
        mode='lines', 
        name=label2
    ))
    
    fig.update_layout(
        title='Performance Comparison',
        xaxis_title='Date',
        yaxis_title='Percentage Change (%)',
        template='plotly_white'
    )
    
    return fig

def main():
    st.title('Global Asset Performance Comparison')
    
    # Sidebar for selections
    st.sidebar.header('Select Asset Comparison')
    
    # Exchange and asset type selection
    region1 = st.sidebar.selectbox('First Region', list(EXCHANGES.keys()))
    asset_type1 = st.sidebar.selectbox('First Asset Type', list(EXCHANGES[region1].keys()))
    asset1 = st.sidebar.selectbox('First Asset', EXCHANGES[region1][asset_type1])
    
    region2 = st.sidebar.selectbox('Second Region', list(EXCHANGES.keys()))
    asset_type2 = st.sidebar.selectbox('Second Asset Type', list(EXCHANGES[region2].keys()))
    asset2 = st.sidebar.selectbox('Second Asset', EXCHANGES[region2][asset_type2])
    
    # Date range selection
    start_date = st.sidebar.date_input('Start Date', pd.Timestamp.now() - pd.DateOffset(years=1))
    end_date = st.sidebar.date_input('End Date', pd.Timestamp.now())
    
    # Fetch and process data
    data1 = fetch_historical_data(asset1, start_date, end_date)
    data2 = fetch_historical_data(asset2, start_date, end_date)
    
    if data1 is not None and data2 is not None:
        # Normalize data
        norm_data1 = normalize_data(data1)
        norm_data2 = normalize_data(data2)
        
        # Calculate correlation
        correlation = calculate_correlation(norm_data1, norm_data2)
        
        # Performance comparison plot
        fig = plot_performance_comparison(norm_data1, norm_data2, asset1, asset2)
        st.plotly_chart(fig, use_container_width=True)
        
        # Display correlation
        st.metric('Correlation Coefficient', f'{correlation:.2f}')
        
        # Additional insights
        st.subheader('Performance Insights')
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric(f'{asset1} Total Return', f'{float(norm_data1.iloc[-1]):.2f}%')
        
        with col2:
            st.metric(f'{asset2} Total Return', f'{float(norm_data2.iloc[-1]):.2f}%')

if __name__ == '__main__':
    main()
