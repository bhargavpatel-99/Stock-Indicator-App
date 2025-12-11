"""
Module D - Trend Analysis
Generates AI-style trend summaries and insights including:
- Price momentum
- Market sentiment summary
- Analyst rating summary
- Trend visualization data
"""

from typing import Dict, List
import pandas as pd
from datetime import datetime


def generate_trend_summary(
    ticker: str,
    indicators: Dict,
    price_data: pd.DataFrame,
    recommendations: List = None,
    news: List = None,
    info: Dict = None
) -> str:
    """
    Generate AI-style trend summary in natural language.
    
    Args:
        ticker: Stock ticker symbol
        indicators: Dictionary from calculate_all_indicators()
        price_data: DataFrame with price data
        recommendations: List of analyst recommendations
        news: List of news items
        info: Stock info dictionary
    
    Returns:
        Formatted trend summary string
    """
    if not indicators.get('success', False) or price_data.empty:
        return f"Insufficient data to generate trend summary for {ticker}."
    
    latest = indicators.get('latest', {})
    indicator_series = indicators.get('indicators', {})
    
    current_price = latest.get('current_price', 0)
    rsi = latest.get('rsi')
    momentum = latest.get('momentum')
    volatility = latest.get('volatility')
    sma_20 = latest.get('sma_20')
    sma_50 = latest.get('sma_50')
    sma_200 = latest.get('sma_200')
    
    summary_parts = []
    
    # Price and Momentum
    if len(price_data) >= 2:
        price_change = ((current_price / price_data['Close'].iloc[-2]) - 1) * 100
        if abs(price_change) > 0.1:
            if price_change > 0:
                summary_parts.append(f"{ticker} is showing positive momentum with a {price_change:.2f}% gain.")
            else:
                summary_parts.append(f"{ticker} is experiencing downward pressure with a {price_change:.2f}% decline.")
    
    # RSI Analysis
    if rsi is not None:
        if rsi < 30:
            summary_parts.append(f"RSI at {rsi:.1f} indicates oversold conditions, potentially signaling a buying opportunity.")
        elif rsi > 70:
            summary_parts.append(f"RSI at {rsi:.1f} suggests overbought territory, indicating potential selling pressure.")
        elif 40 <= rsi <= 60:
            summary_parts.append(f"RSI at {rsi:.1f} suggests balanced market conditions.")
    
    # Moving Average Analysis
    if sma_20 is not None and sma_50 is not None and sma_200 is not None:
        if current_price > sma_20 > sma_50 > sma_200:
            summary_parts.append("Price structure shows strong bullish alignment with all moving averages trending upward.")
        elif current_price < sma_20 < sma_50 < sma_200:
            summary_parts.append("Price structure indicates bearish alignment with all moving averages trending downward.")
        elif sma_50 > sma_200:
            summary_parts.append("SMA50 above SMA200 indicates long-term strength.")
        elif sma_50 < sma_200:
            summary_parts.append("SMA50 below SMA200 suggests long-term weakness.")
    
    # Momentum Analysis
    if momentum is not None:
        if momentum > 10:
            summary_parts.append(f"Strong upward momentum ({momentum:.1f}%) reflects positive investor sentiment.")
        elif momentum < -10:
            summary_parts.append(f"Negative momentum ({momentum:.1f}%) indicates weakening price action.")
        elif -5 <= momentum <= 5:
            summary_parts.append("Momentum is relatively stable, suggesting consolidation.")
    
    # Volatility Analysis
    if volatility is not None:
        if volatility > 30:
            summary_parts.append(f"High volatility ({volatility:.1f}%) indicates significant price swings and market uncertainty.")
        elif volatility < 15:
            summary_parts.append(f"Low volatility ({volatility:.1f}%) suggests stable, predictable price movements.")
    
    # Volume Analysis
    volume_avg = indicator_series.get('volume_avg')
    if volume_avg is not None and not volume_avg.empty and 'Volume' in price_data.columns:
        current_volume = price_data['Volume'].iloc[-1]
        avg_volume = volume_avg.iloc[-1]
        if not pd.isna(avg_volume) and avg_volume > 0:
            volume_ratio = current_volume / avg_volume
            if volume_ratio > 1.5:
                summary_parts.append("Trading volume is significantly above average, indicating strong market interest.")
            elif volume_ratio < 0.5:
                summary_parts.append("Below-average trading volume suggests limited market participation.")
    
    # Analyst Recommendations
    if recommendations:
        recent_recommendations = recommendations[-5:] if len(recommendations) >= 5 else recommendations
        buy_count = sum(1 for rec in recent_recommendations if str(rec.get('toGrade', '')).upper() in ['BUY', 'STRONG BUY', 'OUTPERFORM'])
        hold_count = sum(1 for rec in recent_recommendations if str(rec.get('toGrade', '')).upper() in ['HOLD', 'NEUTRAL'])
        sell_count = sum(1 for rec in recent_recommendations if str(rec.get('toGrade', '')).upper() in ['SELL', 'STRONG SELL', 'UNDERPERFORM'])
        
        if buy_count > 0 or sell_count > 0:
            if buy_count > sell_count:
                summary_parts.append(f"Analyst sentiment is positive with {buy_count} recent buy recommendations.")
            elif sell_count > buy_count:
                summary_parts.append(f"Analyst sentiment is cautious with {sell_count} recent sell recommendations.")
            else:
                summary_parts.append("Analyst recommendations are mixed.")
    
    # News Sentiment
    if news:
        summary_parts.append(f"Recent market news includes {len(news)} articles that may impact sentiment.")
    
    # Company Info
    if info:
        sector = info.get('sector', '')
        industry = info.get('industry', '')
        if sector:
            summary_parts.append(f"Operating in the {sector} sector.")
    
    # Combine all parts
    if summary_parts:
        summary = " ".join(summary_parts)
    else:
        summary = f"{ticker} shows mixed signals with no clear trend direction."
    
    return summary


def get_market_sentiment(news: List = None, recommendations: List = None) -> Dict:
    """
    Extract market sentiment from news and recommendations.
    
    Args:
        news: List of news items
        recommendations: List of analyst recommendations
    
    Returns:
        Dictionary with sentiment analysis
    """
    sentiment = {
        "news_count": len(news) if news else 0,
        "recommendation_summary": {}
    }
    
    if recommendations:
        recent = recommendations[-10:] if len(recommendations) >= 10 else recommendations
        buy_count = sum(1 for rec in recent if str(rec.get('toGrade', '')).upper() in ['BUY', 'STRONG BUY', 'OUTPERFORM'])
        hold_count = sum(1 for rec in recent if str(rec.get('toGrade', '')).upper() in ['HOLD', 'NEUTRAL'])
        sell_count = sum(1 for rec in recent if str(rec.get('toGrade', '')).upper() in ['SELL', 'STRONG SELL', 'UNDERPERFORM'])
        
        sentiment["recommendation_summary"] = {
            "buy": buy_count,
            "hold": hold_count,
            "sell": sell_count,
            "total": len(recent)
        }
    
    return sentiment


def get_price_momentum(price_data: pd.DataFrame, periods: List[int] = [5, 10, 20, 50]) -> Dict:
    """
    Calculate price momentum over multiple periods.
    
    Args:
        price_data: DataFrame with price data
        periods: List of periods (in days) to calculate momentum
    
    Returns:
        Dictionary with momentum for each period
    """
    if price_data.empty or 'Close' not in price_data.columns:
        return {}
    
    current_price = price_data['Close'].iloc[-1]
    momentum_dict = {}
    
    for period in periods:
        if len(price_data) > period:
            past_price = price_data['Close'].iloc[-period-1]
            momentum = ((current_price / past_price) - 1) * 100
            momentum_dict[f"{period}d"] = momentum
    
    return momentum_dict

