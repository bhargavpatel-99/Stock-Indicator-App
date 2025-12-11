"""
Module B - Technical Indicators
Helper functions for calculating:
- SMA (20, 50, 200)
- EMA
- RSI (14)
- Volatility
- Price momentum
"""

import pandas as pd
import numpy as np
from typing import Dict, Optional


def calculate_sma(data: pd.Series, window: int) -> pd.Series:
    """
    Calculate Simple Moving Average.
    
    Args:
        data: Price series (typically Close prices)
        window: Number of periods for SMA
    
    Returns:
        Series with SMA values
    """
    return data.rolling(window=window).mean()


def calculate_ema(data: pd.Series, window: int) -> pd.Series:
    """
    Calculate Exponential Moving Average.
    
    Args:
        data: Price series (typically Close prices)
        window: Number of periods for EMA
    
    Returns:
        Series with EMA values
    """
    return data.ewm(span=window, adjust=False).mean()


def calculate_rsi(data: pd.Series, window: int = 14) -> pd.Series:
    """
    Calculate Relative Strength Index (RSI).
    
    Args:
        data: Price series (typically Close prices)
        window: Number of periods for RSI calculation (default 14)
    
    Returns:
        Series with RSI values (0-100)
    """
    delta = data.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
    
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    
    return rsi


def calculate_volatility(data: pd.Series, window: int = 20) -> pd.Series:
    """
    Calculate volatility (standard deviation of returns).
    
    Args:
        data: Price series (typically Close prices)
        window: Number of periods for volatility calculation
    
    Returns:
        Series with volatility values
    """
    returns = data.pct_change()
    volatility = returns.rolling(window=window).std() * np.sqrt(252) * 100  # Annualized %
    return volatility


def calculate_momentum(data: pd.Series, window: int = 10) -> pd.Series:
    """
    Calculate price momentum (rate of change).
    
    Args:
        data: Price series (typically Close prices)
        window: Number of periods for momentum calculation
    
    Returns:
        Series with momentum values (%)
    """
    momentum = ((data / data.shift(window)) - 1) * 100
    return momentum


def calculate_all_indicators(price_data: pd.DataFrame) -> Dict:
    """
    Calculate all technical indicators for a stock.
    
    Args:
        price_data: DataFrame with OHLCV data (must have 'Close' column)
    
    Returns:
        Dictionary containing all calculated indicators
    """
    if price_data.empty or 'Close' not in price_data.columns:
        return {"error": "Invalid price data"}
    
    close = price_data['Close']
    
    indicators = {
        'sma_20': calculate_sma(close, 20),
        'sma_50': calculate_sma(close, 50),
        'sma_200': calculate_sma(close, 200),
        'ema_12': calculate_ema(close, 12),
        'ema_26': calculate_ema(close, 26),
        'rsi': calculate_rsi(close, 14),
        'volatility': calculate_volatility(close, 20),
        'momentum': calculate_momentum(close, 10),
        'volume_avg': price_data['Volume'].rolling(window=20).mean() if 'Volume' in price_data.columns else None
    }
    
    # Get latest values
    latest = {
        'current_price': close.iloc[-1],
        'sma_20': indicators['sma_20'].iloc[-1] if not pd.isna(indicators['sma_20'].iloc[-1]) else None,
        'sma_50': indicators['sma_50'].iloc[-1] if not pd.isna(indicators['sma_50'].iloc[-1]) else None,
        'sma_200': indicators['sma_200'].iloc[-1] if not pd.isna(indicators['sma_200'].iloc[-1]) else None,
        'rsi': indicators['rsi'].iloc[-1] if not pd.isna(indicators['rsi'].iloc[-1]) else None,
        'volatility': indicators['volatility'].iloc[-1] if not pd.isna(indicators['volatility'].iloc[-1]) else None,
        'momentum': indicators['momentum'].iloc[-1] if not pd.isna(indicators['momentum'].iloc[-1]) else None,
    }
    
    return {
        'indicators': indicators,
        'latest': latest,
        'success': True
    }


def get_price_trend(price_data: pd.DataFrame, sma_20: pd.Series, sma_50: pd.Series) -> str:
    """
    Determine price trend based on moving averages.
    
    Args:
        price_data: DataFrame with price data
        sma_20: SMA(20) series
        sma_50: SMA(50) series
    
    Returns:
        Trend description ('Bullish', 'Bearish', 'Neutral')
    """
    if price_data.empty or sma_20.empty or sma_50.empty:
        return "Neutral"
    
    current_price = price_data['Close'].iloc[-1]
    sma20_val = sma_20.iloc[-1]
    sma50_val = sma_50.iloc[-1]
    
    if pd.isna(sma20_val) or pd.isna(sma50_val):
        return "Neutral"
    
    # Bullish: Price > SMA20 > SMA50
    if current_price > sma20_val > sma50_val:
        return "Bullish"
    # Bearish: Price < SMA20 < SMA50
    elif current_price < sma20_val < sma50_val:
        return "Bearish"
    else:
        return "Neutral"

