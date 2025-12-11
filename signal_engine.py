"""
Module C - Signal Engine
Generates buy/sell/hold recommendations based on:
- Short-term logic (1-14 days)
- Long-term logic (1-12 months)
"""

from typing import Dict, Tuple
import pandas as pd
import numpy as np


def generate_short_term_signal(indicators: Dict, price_data: pd.DataFrame) -> Tuple[str, str]:
    """
    Generate short-term buy/sell/hold signal (1-14 days).
    
    Logic:
    - RSI < 30 → Short-term Buy (oversold)
    - RSI > 70 → Short-term Sell (overbought)
    - Price crossing above SMA20 → Bullish
    - Price crossing below SMA20 → Bearish
    - Momentum > 5% → Bullish
    - Momentum < -5% → Bearish
    
    Args:
        indicators: Dictionary from calculate_all_indicators()
        price_data: DataFrame with price data
    
    Returns:
        Tuple of (signal, reason)
    """
    if not indicators.get('success', False):
        return "HOLD", "Insufficient data for analysis"
    
    latest = indicators.get('latest', {})
    indicator_series = indicators.get('indicators', {})
    
    current_price = latest.get('current_price', 0)
    rsi = latest.get('rsi')
    momentum = latest.get('momentum')
    sma_20 = latest.get('sma_20')
    
    reasons = []
    buy_score = 0
    sell_score = 0
    
    # RSI Analysis
    if rsi is not None:
        if rsi < 30:
            buy_score += 2
            reasons.append(f"RSI = {rsi:.1f} (oversold)")
        elif rsi > 70:
            sell_score += 2
            reasons.append(f"RSI = {rsi:.1f} (overbought)")
        elif 30 <= rsi <= 40:
            buy_score += 1
            reasons.append(f"RSI = {rsi:.1f} (approaching oversold)")
        elif 60 <= rsi <= 70:
            sell_score += 1
            reasons.append(f"RSI = {rsi:.1f} (approaching overbought)")
    
    # Price vs SMA20 Analysis
    if sma_20 is not None and current_price > 0:
        sma_20_series = indicator_series.get('sma_20', pd.Series())
        if not sma_20_series.empty and len(sma_20_series) >= 2:
            # Check if price crossed above SMA20
            prev_price = price_data['Close'].iloc[-2] if len(price_data) >= 2 else current_price
            prev_sma20 = sma_20_series.iloc[-2] if len(sma_20_series) >= 2 else sma_20
            
            if prev_price <= prev_sma20 and current_price > sma_20:
                buy_score += 2
                reasons.append("Price crossed above SMA20 (bullish breakout)")
            elif prev_price >= prev_sma20 and current_price < sma_20:
                sell_score += 2
                reasons.append("Price crossed below SMA20 (bearish breakdown)")
            elif current_price > sma_20 * 1.02:
                buy_score += 1
                reasons.append("Price significantly above SMA20")
            elif current_price < sma_20 * 0.98:
                sell_score += 1
                reasons.append("Price significantly below SMA20")
    
    # Momentum Analysis
    if momentum is not None:
        if momentum > 5:
            buy_score += 1
            reasons.append(f"Strong positive momentum ({momentum:.1f}%)")
        elif momentum < -5:
            sell_score += 1
            reasons.append(f"Strong negative momentum ({momentum:.1f}%)")
    
    # Volume Analysis
    volume_avg = indicator_series.get('volume_avg')
    if volume_avg is not None and not volume_avg.empty and 'Volume' in price_data.columns:
        current_volume = price_data['Volume'].iloc[-1]
        avg_volume = volume_avg.iloc[-1]
        if not pd.isna(avg_volume) and avg_volume > 0:
            volume_ratio = current_volume / avg_volume
            if volume_ratio > 1.5:
                if buy_score > sell_score:
                    reasons.append("High volume confirms bullish move")
                elif sell_score > buy_score:
                    reasons.append("High volume confirms bearish move")
    
    # Determine signal
    if buy_score > sell_score and buy_score >= 2:
        signal = "BUY"
    elif sell_score > buy_score and sell_score >= 2:
        signal = "SELL"
    else:
        signal = "HOLD"
    
    reason = ", ".join(reasons) if reasons else "Neutral technical indicators"
    
    return signal, reason


def generate_long_term_signal(indicators: Dict, price_data: pd.DataFrame, recommendations: list = None) -> Tuple[str, str]:
    """
    Generate long-term buy/sell/hold signal (1-12 months).
    
    Logic:
    - Price > SMA200 and SMA50 trending upward → Long-term Buy
    - Price < SMA200 → Long-term Caution/Sell
    - Strong upward multi-month momentum → Long-term Buy
    - Weak fundamentals (analyst downgrades) → Long-term caution
    
    Args:
        indicators: Dictionary from calculate_all_indicators()
        price_data: DataFrame with price data
        recommendations: List of analyst recommendations
    
    Returns:
        Tuple of (signal, reason)
    """
    if not indicators.get('success', False):
        return "HOLD", "Insufficient data for analysis"
    
    latest = indicators.get('latest', {})
    indicator_series = indicators.get('indicators', {})
    
    current_price = latest.get('current_price', 0)
    sma_50 = latest.get('sma_50')
    sma_200 = latest.get('sma_200')
    momentum = latest.get('momentum')
    
    reasons = []
    buy_score = 0
    sell_score = 0
    
    # SMA200 Analysis (long-term trend)
    if sma_200 is not None and current_price > 0:
        if current_price > sma_200:
            buy_score += 3
            reasons.append(f"Price ({current_price:.2f}) above SMA200 ({sma_200:.2f}) - long-term uptrend")
        else:
            sell_score += 2
            reasons.append(f"Price ({current_price:.2f}) below SMA200 ({sma_200:.2f}) - long-term downtrend")
    
    # SMA50 vs SMA200 Analysis (Golden/Death Cross)
    if sma_50 is not None and sma_200 is not None:
        sma_50_series = indicator_series.get('sma_50', pd.Series())
        sma_200_series = indicator_series.get('sma_200', pd.Series())
        
        if not sma_50_series.empty and not sma_200_series.empty and len(sma_50_series) >= 2:
            prev_sma50 = sma_50_series.iloc[-2]
            prev_sma200 = sma_200_series.iloc[-2] if len(sma_200_series) >= 2 else sma_200
            
            # Golden Cross: SMA50 crosses above SMA200
            if prev_sma50 <= prev_sma200 and sma_50 > sma_200:
                buy_score += 3
                reasons.append("Golden Cross detected (SMA50 > SMA200) - strong bullish signal")
            # Death Cross: SMA50 crosses below SMA200
            elif prev_sma50 >= prev_sma200 and sma_50 < sma_200:
                sell_score += 3
                reasons.append("Death Cross detected (SMA50 < SMA200) - strong bearish signal")
            elif sma_50 > sma_200:
                buy_score += 1
                reasons.append("SMA50 above SMA200 - positive trend")
            elif sma_50 < sma_200:
                sell_score += 1
                reasons.append("SMA50 below SMA200 - negative trend")
    
    # Long-term Momentum Analysis
    if momentum is not None:
        if momentum > 10:
            buy_score += 2
            reasons.append(f"Strong long-term momentum ({momentum:.1f}%)")
        elif momentum < -10:
            sell_score += 2
            reasons.append(f"Weak long-term momentum ({momentum:.1f}%)")
    
    # Analyst Recommendations Analysis
    if recommendations:
        recent_recommendations = recommendations[-5:] if len(recommendations) >= 5 else recommendations
        buy_count = sum(1 for rec in recent_recommendations if rec.get('toGrade', '').upper() in ['BUY', 'STRONG BUY', 'OUTPERFORM'])
        sell_count = sum(1 for rec in recent_recommendations if rec.get('toGrade', '').upper() in ['SELL', 'STRONG SELL', 'UNDERPERFORM'])
        
        if buy_count > sell_count * 2:
            buy_score += 1
            reasons.append(f"Analyst sentiment: {buy_count} buy recommendations")
        elif sell_count > buy_count * 2:
            sell_score += 1
            reasons.append(f"Analyst sentiment: {sell_count} sell recommendations")
    
    # Determine signal
    if buy_score >= 4:
        signal = "BUY"
    elif sell_score >= 4:
        signal = "SELL"
    elif buy_score > sell_score:
        signal = "HOLD (Bullish)"
    elif sell_score > buy_score:
        signal = "HOLD (Bearish)"
    else:
        signal = "HOLD"
    
    reason = ", ".join(reasons) if reasons else "Mixed long-term indicators"
    
    return signal, reason

