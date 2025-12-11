"""
Module A - Data Fetching
Fetches stock data using yfinance including:
- Price OHLC
- Volume
- Moving averages
- RSI
- Analyst recommendations
- Market news
"""

import yfinance as yf
import pandas as pd
from typing import Dict, Optional, Tuple, List
from datetime import datetime, timedelta
import feedparser
import requests
from bs4 import BeautifulSoup
import time


def get_stock_data(ticker: str, period: str = "1y") -> Dict:
    """
    Fetch comprehensive stock data for a given ticker.
    
    Args:
        ticker: Stock ticker symbol (e.g., 'AAPL', 'MSFT')
        period: Time period for historical data ('1d', '5d', '1mo', '3mo', '6mo', '1y', '2y', '5y', '10y', 'ytd', 'max')
    
    Returns:
        Dictionary containing:
        - price_data: DataFrame with OHLCV data
        - current_price: Current stock price
        - info: Stock info dictionary
        - recommendations: Analyst recommendations
        - news: Market news
        - history: Historical price data
    """
    try:
        stock = yf.Ticker(ticker)
        
        # Fetch historical data
        hist = stock.history(period=period)
        
        if hist.empty:
            return {"error": f"No data found for ticker {ticker}"}
        
        # Get current info
        info = stock.info
        
        # Get current price (use last close price if current price unavailable)
        current_price = hist['Close'].iloc[-1] if not hist.empty else None
        
        # Get analyst recommendations
        try:
            recommendations = stock.recommendations
            if recommendations is not None and not recommendations.empty:
                recommendations = recommendations.tail(10).to_dict('records')
            else:
                recommendations = []
        except:
            recommendations = []
        
        # Get news - try multiple sources
        news = []
        
        # Try yfinance news first (primary source)
        try:
            yf_news = stock.news
            if yf_news:
                for item in yf_news[:10]:  # Get up to 10 items
                    try:
                        # yfinance news structure: item['content'] contains the actual news data
                        content = item.get('content', {})
                        if not content:
                            continue
                        
                        title = content.get('title', '').strip()
                        if not title:
                            continue
                        
                        # Extract publisher from provider object
                        publisher = 'Yahoo Finance'
                        provider = content.get('provider', {})
                        if isinstance(provider, dict):
                            publisher = provider.get('displayName', provider.get('name', 'Yahoo Finance'))
                        elif isinstance(provider, str):
                            publisher = provider
                        
                        # Extract link from canonicalUrl or clickThroughUrl
                        link = ''
                        canonical_url = content.get('canonicalUrl', {})
                        click_through_url = content.get('clickThroughUrl', {})
                        
                        if isinstance(canonical_url, dict) and canonical_url.get('url'):
                            link = canonical_url['url']
                        elif isinstance(click_through_url, dict) and click_through_url.get('url'):
                            link = click_through_url['url']
                        elif isinstance(canonical_url, str):
                            link = canonical_url
                        elif isinstance(click_through_url, str):
                            link = click_through_url
                        
                        if not link:
                            link = f"https://finance.yahoo.com/quote/{ticker}/news"
                        
                        # Extract published date (pubDate is in ISO format: "2025-12-10T18:13:49Z")
                        published = None
                        pub_date = content.get('pubDate', '')
                        if pub_date:
                            try:
                                # Try parsing ISO format
                                if 'T' in pub_date:
                                    # Remove timezone info if present
                                    pub_date_clean = pub_date.split('+')[0].split('Z')[0]
                                    published = datetime.strptime(pub_date_clean, '%Y-%m-%dT%H:%M:%S')
                                else:
                                    published = datetime.strptime(pub_date, '%Y-%m-%d')
                            except:
                                try:
                                    # Try timestamp format
                                    if isinstance(pub_date, (int, float)):
                                        published = datetime.fromtimestamp(pub_date)
                                except:
                                    pass
                        
                        news.append({
                            'title': title,
                            'publisher': publisher,
                            'link': link,
                            'published': published
                        })
                    except Exception as e:
                        continue
        except Exception as e:
            pass
        
        # If no news from yfinance, try RSS feeds as fallback
        if not news:
            try:
                rss_news = fetch_yahoo_finance_news(ticker)
                if rss_news:
                    news = rss_news[:10]
            except:
                pass
        
        # If still no news, try web scraping as last resort
        if not news:
            try:
                alt_news = fetch_stock_news_alternative(ticker, info.get('longName', ''))
                if alt_news:
                    news = alt_news[:10]
            except:
                pass
        
        # Prepare price data
        price_data = hist.copy()
        price_data.reset_index(inplace=True)
        
        return {
            "ticker": ticker.upper(),
            "price_data": hist,
            "current_price": current_price,
            "info": info,
            "recommendations": recommendations,
            "news": news,
            "history": hist,
            "success": True
        }
    
    except Exception as e:
        return {
            "error": f"Error fetching data for {ticker}: {str(e)}",
            "success": False
        }


def get_stock_info(ticker: str) -> Dict:
    """
    Get basic stock information.
    
    Args:
        ticker: Stock ticker symbol
    
    Returns:
        Dictionary with stock info
    """
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        
        return {
            "ticker": ticker.upper(),
            "name": info.get('longName', ticker),
            "sector": info.get('sector', 'N/A'),
            "industry": info.get('industry', 'N/A'),
            "market_cap": info.get('marketCap', 0),
            "pe_ratio": info.get('trailingPE', None),
            "dividend_yield": info.get('dividendYield', None),
            "52_week_high": info.get('fiftyTwoWeekHigh', None),
            "52_week_low": info.get('fiftyTwoWeekLow', None),
            "success": True
        }
    except Exception as e:
        return {
            "error": f"Error fetching info for {ticker}: {str(e)}",
            "success": False
        }


def fetch_yahoo_finance_news(ticker: str) -> List[Dict]:
    """
    Fetch news from Yahoo Finance RSS feed and Google News.
    
    Args:
        ticker: Stock ticker symbol
    
    Returns:
        List of news dictionaries
    """
    news_items = []
    
    # Try multiple Yahoo Finance RSS feed formats
    rss_urls = [
        f"https://feeds.finance.yahoo.com/rss/2.0/headline?s={ticker}&region=US&lang=en-US",
        f"https://finance.yahoo.com/rss/headline?s={ticker}",
    ]
    
    for rss_url in rss_urls:
        try:
            feed = feedparser.parse(rss_url)
            
            if feed.entries:
                for entry in feed.entries[:10]:
                    try:
                        # Parse published date
                        published = None
                        if hasattr(entry, 'published_parsed') and entry.published_parsed:
                            published = datetime(*entry.published_parsed[:6])
                        elif hasattr(entry, 'published'):
                            try:
                                published = datetime.strptime(entry.published, '%a, %d %b %Y %H:%M:%S %z')
                            except:
                                try:
                                    published = datetime.strptime(entry.published, '%a, %d %b %Y %H:%M:%S %Z')
                                except:
                                    pass
                        
                        title = entry.get('title', '').strip()
                        link = entry.get('link', '').strip()
                        
                        if title and link:
                            publisher = 'Yahoo Finance'
                            if hasattr(entry, 'source') and entry.source:
                                publisher = entry.source.get('title', 'Yahoo Finance') if isinstance(entry.source, dict) else str(entry.source)
                            
                            news_items.append({
                                'title': title,
                                'publisher': publisher,
                                'link': link,
                                'published': published
                            })
                    except Exception as e:
                        continue
                
                if news_items:  # If we got results, break
                    break
        except Exception as e:
            continue
    
    # If no Yahoo Finance news, try Google News RSS
    if not news_items:
        try:
            search_query = f"{ticker} stock news"
            google_news_url = f"https://news.google.com/rss/search?q={search_query}&hl=en-US&gl=US&ceid=US:en"
            
            feed = feedparser.parse(google_news_url)
            
            if feed.entries:
                for entry in feed.entries[:10]:
                    try:
                        published = None
                        if hasattr(entry, 'published_parsed') and entry.published_parsed:
                            published = datetime(*entry.published_parsed[:6])
                        
                        title = entry.get('title', '').strip()
                        link = entry.get('link', '').strip()
                        
                        if title and link:
                            publisher = 'Google News'
                            if hasattr(entry, 'source') and entry.source:
                                publisher = entry.source.get('title', 'Google News') if isinstance(entry.source, dict) else str(entry.source)
                            
                            news_items.append({
                                'title': title,
                                'publisher': publisher,
                                'link': link,
                                'published': published
                            })
                    except:
                        continue
        except:
            pass
    
    return news_items


def fetch_stock_news_alternative(ticker: str, company_name: str = "") -> List[Dict]:
    """
    Fetch news using alternative methods (web scraping Yahoo Finance news page).
    
    Args:
        ticker: Stock ticker symbol
        company_name: Company name for better search
    
    Returns:
        List of news dictionaries
    """
    news_items = []
    
    try:
        # Try Yahoo Finance news page
        url = f"https://finance.yahoo.com/quote/{ticker}/news"
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Look for news articles in the page
            # Yahoo Finance uses various selectors, try common ones
            articles = soup.find_all(['article', 'div'], class_=lambda x: x and ('news' in x.lower() or 'story' in x.lower()))
            
            if not articles:
                # Try alternative selectors
                articles = soup.find_all('h3', class_=lambda x: x and 'Mb(5px)' in str(x))
            
            for article in articles[:10]:
                try:
                    # Extract title and link
                    link_elem = article.find('a', href=True)
                    title_elem = article.find(['h3', 'h2', 'span'], class_=lambda x: x and 'title' in str(x).lower()) or article.find('a')
                    
                    if link_elem:
                        link = link_elem.get('href', '')
                        if link and not link.startswith('http'):
                            link = f"https://finance.yahoo.com{link}"
                        
                        title = title_elem.get_text(strip=True) if title_elem else link_elem.get_text(strip=True)
                        
                        if title and link:
                            news_items.append({
                                'title': title,
                                'publisher': 'Yahoo Finance',
                                'link': link,
                                'published': None  # Date parsing from HTML is complex
                            })
                except:
                    continue
    except Exception as e:
        pass
    
    # If still no news, try Google News RSS (as fallback)
    if not news_items:
        try:
            search_query = f"{ticker} stock" if not company_name else f"{company_name} {ticker}"
            google_news_url = f"https://news.google.com/rss/search?q={search_query}&hl=en-US&gl=US&ceid=US:en"
            
            feed = feedparser.parse(google_news_url)
            
            if feed.entries:
                for entry in feed.entries[:10]:
                    try:
                        published = None
                        if hasattr(entry, 'published_parsed') and entry.published_parsed:
                            published = datetime(*entry.published_parsed[:6])
                        
                        news_items.append({
                            'title': entry.get('title', ''),
                            'publisher': entry.get('source', {}).get('title', 'Google News') if hasattr(entry, 'source') else 'Google News',
                            'link': entry.get('link', ''),
                            'published': published
                        })
                    except:
                        continue
        except:
            pass
    
    return news_items


def search_stock(query: str) -> list:
    """
    Search for stocks by ticker or name.
    Note: yfinance doesn't have built-in search, so this is a simple ticker validation.
    For production, you'd want to integrate with a stock search API.
    
    Args:
        query: Search query (ticker or name)
    
    Returns:
        List of matching tickers
    """
    # Simple validation - try to fetch the ticker
    # In production, integrate with a proper search API
    try:
        stock = yf.Ticker(query.upper())
        info = stock.info
        if info and 'symbol' in info:
            return [{
                "ticker": query.upper(),
                "name": info.get('longName', query.upper()),
                "exchange": info.get('exchange', 'N/A')
            }]
    except:
        pass
    
    return []

