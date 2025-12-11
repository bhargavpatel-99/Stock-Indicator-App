# Stock Indicator App 📈

A comprehensive Python application for stock market analysis with real-time data, technical indicators, and AI-powered buy/sell/hold signals.

## Features

- 🔍 **Stock Search**: Search and analyze any stock by ticker symbol
- 📊 **Real-time Data**: Fetch live stock prices and historical data using yfinance
- 📈 **Technical Indicators**: 
  - Simple Moving Averages (SMA 20, 50, 200)
  - Exponential Moving Averages (EMA 12, 26)
  - Relative Strength Index (RSI)
  - Volatility calculations
  - Price momentum analysis
- 🎯 **Trading Signals**:
  - Short-term signals (1-14 days)
  - Long-term signals (1-12 months)
  - Data-driven reasoning for each recommendation
- 💡 **Trend Insights**: AI-style summaries of stock performance and market sentiment
- 📰 **Market News**: Recent news articles and analyst recommendations
- 📉 **Interactive Charts**: Visualize price trends and indicators with Plotly

## Installation

1. Clone or download this repository
2. Install dependencies:

```bash
pip install -r requirements.txt
```

## Usage

Run the Streamlit app:

```bash
streamlit run app.py
```

Or if you need to specify python3:

```bash
python3 -m streamlit run app.py
```

The app will open in your browser. Enter a stock ticker (e.g., AAPL, MSFT, TSLA) in the sidebar and click "Analyze Stock".

## Project Structure

```
/app
  ├── app.py                 # Main Streamlit application
  ├── data_fetcher.py        # Module A - Data fetching with yfinance
  ├── indicators.py          # Module B - Technical indicators
  ├── signal_engine.py       # Module C - Buy/sell/hold signals
  ├── trend_analysis.py       # Module D - Trend summaries and insights
  ├── requirements.txt       # Python dependencies
  └── README.md             # This file
```

## Modules

### Module A - Data Fetcher (`data_fetcher.py`)
- Fetches stock data using yfinance
- Retrieves OHLCV data, analyst recommendations, and news
- Handles errors gracefully

### Module B - Indicators (`indicators.py`)
- Calculates SMA, EMA, RSI, volatility, and momentum
- Provides trend analysis functions

### Module C - Signal Engine (`signal_engine.py`)
- Generates short-term trading signals based on RSI, moving averages, and momentum
- Generates long-term signals based on SMA200, Golden/Death Cross, and analyst sentiment

### Module D - Trend Analysis (`trend_analysis.py`)
- Creates natural language trend summaries
- Analyzes market sentiment
- Calculates multi-period momentum

## Example Usage

1. **Search a Stock**: Enter "AAPL" in the sidebar
2. **View Overview**: See current price, RSI, volatility, and company info
3. **Analyze Charts**: View price trends with moving averages and RSI
4. **Get Signals**: See short-term and long-term buy/sell/hold recommendations
5. **Read Insights**: Understand what's happening with the stock through AI-style summaries

## Dependencies

- `yfinance==0.2.66` - Stock data fetching
- `streamlit==1.28.0` - Web UI framework
- `pandas==2.1.3` - Data manipulation
- `numpy==1.26.2` - Numerical computations
- `plotly==5.18.0` - Interactive charts
- `ta==0.11.0` - Technical analysis (optional, for additional indicators)

## Notes

- Stock data is fetched in real-time from Yahoo Finance
- Some stocks may have limited data availability
- Analyst recommendations and news depend on data availability from yfinance
- Always do your own research before making investment decisions

## 🚀 Deployment

### Deploy to Streamlit Cloud (Free)

1. **Fork or ensure your repository is on GitHub**
   - Repository: https://github.com/bhargavpatel-99/Stock-Indicator-App

2. **Go to Streamlit Cloud**
   - Visit: https://share.streamlit.io/
   - Sign in with your GitHub account

3. **Deploy your app**
   - Click "New app"
   - Select your repository: `bhargavpatel-99/Stock-Indicator-App`
   - Branch: `main`
   - Main file path: `app.py`
   - Click "Deploy"

4. **Your app will be live!**
   - Streamlit Cloud will provide you with a public URL
   - Example: `https://stock-indicator-app.streamlit.app`

### Alternative Deployment Options

- **Heroku**: Use Procfile and requirements.txt
- **AWS/GCP/Azure**: Deploy as a containerized app
- **Docker**: Containerize and deploy anywhere

## License

This project is for educational purposes only. Not financial advice.

