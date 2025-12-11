"""
Main Streamlit Application
Stock Indicator App with Search, Signals, and Trend Insights
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
from typing import Dict

from data_fetcher import get_stock_data, get_stock_info
from indicators import calculate_all_indicators, get_price_trend
from signal_engine import generate_short_term_signal, generate_long_term_signal
from trend_analysis import generate_trend_summary, get_market_sentiment, get_price_momentum
from stock_search import search_stocks, get_all_stocks, get_stock_display_name


# Page configuration
st.set_page_config(
    page_title="Stock Indicator App",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .signal-box {
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .signal-buy {
        background-color: #d4edda;
        border: 2px solid #28a745;
    }
    .signal-sell {
        background-color: #f8d7da;
        border: 2px solid #dc3545;
    }
    .signal-hold {
        background-color: #fff3cd;
        border: 2px solid #ffc107;
    }
    .metric-card {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
    </style>
""", unsafe_allow_html=True)


def create_price_chart(price_data: pd.DataFrame, indicators: Dict):
    """Create interactive price chart with moving averages."""
    fig = make_subplots(
        rows=2, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.03,
        subplot_titles=('Price & Moving Averages', 'RSI'),
        row_width=[0.7, 0.3]
    )
    
    # Price and Moving Averages
    fig.add_trace(
        go.Scatter(x=price_data.index, y=price_data['Close'], name='Close Price', line=dict(color='#1f77b4', width=2)),
        row=1, col=1
    )
    
    indicator_series = indicators.get('indicators', {})
    
    if 'sma_20' in indicator_series and not indicator_series['sma_20'].empty:
        fig.add_trace(
            go.Scatter(x=price_data.index, y=indicator_series['sma_20'], name='SMA 20', line=dict(color='orange', width=1)),
            row=1, col=1
        )
    
    if 'sma_50' in indicator_series and not indicator_series['sma_50'].empty:
        fig.add_trace(
            go.Scatter(x=price_data.index, y=indicator_series['sma_50'], name='SMA 50', line=dict(color='green', width=1)),
            row=1, col=1
        )
    
    if 'sma_200' in indicator_series and not indicator_series['sma_200'].empty:
        fig.add_trace(
            go.Scatter(x=price_data.index, y=indicator_series['sma_200'], name='SMA 200', line=dict(color='red', width=1)),
            row=1, col=1
        )
    
    # RSI
    if 'rsi' in indicator_series and not indicator_series['rsi'].empty:
        fig.add_trace(
            go.Scatter(x=price_data.index, y=indicator_series['rsi'], name='RSI', line=dict(color='purple', width=1)),
            row=2, col=1
        )
        # Add RSI reference lines
        fig.add_hline(y=70, line_dash="dash", line_color="red", opacity=0.5, row=2, col=1)
        fig.add_hline(y=30, line_dash="dash", line_color="green", opacity=0.5, row=2, col=1)
        fig.add_hline(y=50, line_dash="dot", line_color="gray", opacity=0.3, row=2, col=1)
    
    fig.update_layout(
        height=600,
        showlegend=True,
        hovermode='x unified',
        title_text="Stock Analysis Chart"
    )
    
    fig.update_xaxes(title_text="Date", row=2, col=1)
    fig.update_yaxes(title_text="Price ($)", row=1, col=1)
    fig.update_yaxes(title_text="RSI", row=2, col=1)
    
    return fig


def main():
    st.markdown('<div class="main-header">📈 Stock Indicator App</div>', unsafe_allow_html=True)
    
    # Sidebar
    st.sidebar.header("Stock Search")
    
    # Search input for filtering stocks
    search_query = st.sidebar.text_input(
        "🔍 Search by Ticker or Company Name", 
        value=st.session_state.get('search_query', ''),
        placeholder="Type to search... (e.g., Apple, AAPL, Microsoft)"
    )
    
    # Update session state for search query
    if search_query != st.session_state.get('search_query', ''):
        st.session_state['search_query'] = search_query
    
    # Get filtered stocks based on search, or all stocks if no search
    if search_query:
        stock_options = search_stocks(search_query, limit=100)
    else:
        stock_options = get_all_stocks()
    
    # Create formatted options for selectbox: "TICKER - Company Name"
    if stock_options:
        selectbox_options = [f"{stock['ticker']} - {stock['name']}" for stock in stock_options]
    else:
        selectbox_options = []
    
    # Add manual entry option at the beginning
    selectbox_options.insert(0, "📝 Enter ticker manually")
    
    # Find current selection index
    current_ticker = st.session_state.get('ticker', 'AAPL')
    current_index = 0
    if current_ticker:
        # Try to find current ticker in options
        for i, opt in enumerate(selectbox_options):
            if opt.startswith(current_ticker + " -") or (opt == "📝 Enter ticker manually" and i == 0):
                current_index = i
                break
    
    # Stock selection dropdown
    selected_option = st.sidebar.selectbox(
        "Select Stock",
        options=selectbox_options,
        index=current_index,
        help="Search above to filter, or select from the list"
    )
    
    # Handle ticker extraction
    if selected_option == "📝 Enter ticker manually":
        # Manual entry mode
        ticker_input = st.sidebar.text_input(
            "Enter Stock Ticker",
            value=current_ticker if current_ticker else '',
            placeholder="e.g., AAPL, MSFT, TSLA"
        )
    else:
        # Extract ticker from selected option
        ticker_input = selected_option.split(" - ")[0].strip()
    
    # Time period selection
    period_select = st.sidebar.selectbox("Time Period", ["1mo", "3mo", "6mo", "1y", "2y"], index=3)
    
    # Analyze button
    if st.sidebar.button("Analyze Stock", type="primary"):
        if ticker_input and ticker_input.strip():
            st.session_state['ticker'] = ticker_input.upper().strip()
            st.session_state['period'] = period_select
        else:
            st.sidebar.warning("⚠️ Please enter or select a stock ticker")
    
    # Use session state or default
    ticker = st.session_state.get('ticker', 'AAPL')
    period = st.session_state.get('period', '1y')
    
    if not ticker:
        st.info("👈 Please enter a stock ticker in the sidebar to get started.")
        return
    
    # Fetch data
    with st.spinner(f"Fetching data for {ticker}..."):
        stock_data = get_stock_data(ticker, period)
    
    if not stock_data.get('success', False):
        st.error(f"❌ Error: {stock_data.get('error', 'Failed to fetch stock data')}")
        st.info("💡 Try a different ticker symbol (e.g., AAPL, MSFT, GOOGL, TSLA)")
        return
    
    price_data = stock_data['price_data']
    current_price = stock_data['current_price']
    info = stock_data.get('info', {})
    recommendations = stock_data.get('recommendations', [])
    news = stock_data.get('news', [])
    
    # Calculate indicators
    with st.spinner("Calculating technical indicators..."):
        indicators = calculate_all_indicators(price_data)
    
    if not indicators.get('success', False):
        st.error("Failed to calculate indicators")
        return
    
    latest = indicators['latest']
    
    # Header with current price
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Current Price", f"${current_price:.2f}" if current_price else "N/A")
    with col2:
        rsi_val = latest.get('rsi')
        rsi_color = "normal"
        if rsi_val:
            if rsi_val < 30:
                rsi_color = "inverse"
            elif rsi_val > 70:
                rsi_color = "off"
        st.metric("RSI", f"{rsi_val:.1f}" if rsi_val else "N/A", delta=None)
    with col3:
        sma_200 = latest.get('sma_200')
        st.metric("SMA 200", f"${sma_200:.2f}" if sma_200 else "N/A")
    with col4:
        volatility = latest.get('volatility')
        st.metric("Volatility", f"{volatility:.1f}%" if volatility else "N/A")
    
    st.divider()
    
    # Main content tabs
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Overview", "📈 Charts", "🎯 Signals", "📰 Insights"])
    
    with tab1:
        st.subheader("Stock Overview")
        
        # Stock info
        col1, col2 = st.columns(2)
        with col1:
            st.write(f"**Ticker:** {ticker}")
            st.write(f"**Company:** {info.get('longName', 'N/A')}")
            st.write(f"**Sector:** {info.get('sector', 'N/A')}")
            st.write(f"**Industry:** {info.get('industry', 'N/A')}")
        
        with col2:
            market_cap = info.get('marketCap', 0)
            if market_cap:
                market_cap_b = market_cap / 1e9
                st.write(f"**Market Cap:** ${market_cap_b:.2f}B")
            st.write(f"**PE Ratio:** {info.get('trailingPE', 'N/A')}")
            st.write(f"**52W High:** ${info.get('fiftyTwoWeekHigh', 'N/A')}")
            st.write(f"**52W Low:** ${info.get('fiftyTwoWeekLow', 'N/A')}")
        
        st.divider()
        
        # Technical Indicators
        st.subheader("Technical Indicators")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("SMA 20", f"${latest.get('sma_20', 0):.2f}" if latest.get('sma_20') else "N/A")
        with col2:
            st.metric("SMA 50", f"${latest.get('sma_50', 0):.2f}" if latest.get('sma_50') else "N/A")
        with col3:
            momentum = latest.get('momentum')
            st.metric("Momentum (10d)", f"{momentum:.1f}%" if momentum else "N/A")
        with col4:
            trend = get_price_trend(price_data, indicators['indicators']['sma_20'], indicators['indicators']['sma_50'])
            st.metric("Trend", trend)
    
    with tab2:
        st.subheader("Price Chart & Indicators")
        fig = create_price_chart(price_data, indicators)
        st.plotly_chart(fig, use_container_width=True)
    
    with tab3:
        st.subheader("Trading Signals")
        
        # Generate signals
        short_signal, short_reason = generate_short_term_signal(indicators, price_data)
        long_signal, long_reason = generate_long_term_signal(indicators, price_data, recommendations)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### Short-Term Signal (1-14 days)")
            signal_class = "signal-buy" if short_signal == "BUY" else "signal-sell" if short_signal == "SELL" else "signal-hold"
            st.markdown(f'<div class="signal-box {signal_class}">', unsafe_allow_html=True)
            st.markdown(f"**Signal:** {short_signal}")
            st.markdown(f"**Reason:** {short_reason}")
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            st.markdown("### Long-Term Signal (1-12 months)")
            signal_class = "signal-buy" if "BUY" in long_signal else "signal-sell" if "SELL" in long_signal else "signal-hold"
            st.markdown(f'<div class="signal-box {signal_class}">', unsafe_allow_html=True)
            st.markdown(f"**Signal:** {long_signal}")
            st.markdown(f"**Reason:** {long_reason}")
            st.markdown('</div>', unsafe_allow_html=True)
        
        st.divider()
        
        # Signal details
        st.markdown("### Signal Analysis Details")
        st.json({
            "short_term": {
                "signal": short_signal,
                "reasoning": short_reason
            },
            "long_term": {
                "signal": long_signal,
                "reasoning": long_reason
            }
        })
    
    with tab4:
        st.subheader("What's Going On With This Stock?")
        
        # Trend Summary
        trend_summary = generate_trend_summary(ticker, indicators, price_data, recommendations, news, info)
        st.markdown("### 📊 Trend Summary")
        st.info(trend_summary)
        
        st.divider()
        
        # Price Momentum
        st.markdown("### 📈 Price Momentum")
        momentum_data = get_price_momentum(price_data)
        if momentum_data:
            momentum_df = pd.DataFrame(list(momentum_data.items()), columns=['Period', 'Momentum %'])
            st.dataframe(momentum_df, use_container_width=True)
        
        st.divider()
        
        # Market Sentiment
        st.markdown("### 💭 Market Sentiment")
        sentiment = get_market_sentiment(news, recommendations)
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Recent News Articles", sentiment['news_count'])
        with col2:
            rec_summary = sentiment.get('recommendation_summary', {})
            if rec_summary:
                st.write(f"**Analyst Recommendations:**")
                st.write(f"- Buy: {rec_summary.get('buy', 0)}")
                st.write(f"- Hold: {rec_summary.get('hold', 0)}")
                st.write(f"- Sell: {rec_summary.get('sell', 0)}")
        
        st.divider()
        
        # Recent News
        if news:
            st.markdown("### 📰 Recent News")
            for item in news[:5]:
                with st.expander(item.get('title', 'No title')):
                    st.write(f"**Publisher:** {item.get('publisher', 'N/A')}")
                    if item.get('published'):
                        st.write(f"**Published:** {item['published'].strftime('%Y-%m-%d %H:%M')}")
                    if item.get('link'):
                        st.markdown(f"[Read more]({item['link']})")
        
        # Analyst Recommendations
        if recommendations:
            st.markdown("### 🎯 Analyst Recommendations")
            rec_df = pd.DataFrame(recommendations[-10:])
            if not rec_df.empty:
                # Clean up the dataframe for display
                display_cols = []
                for col in ['firm', 'toGrade', 'fromGrade', 'action']:
                    if col in rec_df.columns:
                        display_cols.append(col)
                
                if display_cols:
                    st.dataframe(rec_df[display_cols], use_container_width=True)


if __name__ == "__main__":
    main()

