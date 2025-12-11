"""
Stock Search Module
Provides searchable stock database with ticker and company name matching
"""

# Popular stocks database - ticker: (company_name, sector)
POPULAR_STOCKS = {
    # Technology
    "AAPL": ("Apple Inc.", "Technology"),
    "MSFT": ("Microsoft Corporation", "Technology"),
    "GOOGL": ("Alphabet Inc.", "Technology"),
    "GOOG": ("Alphabet Inc.", "Technology"),
    "AMZN": ("Amazon.com Inc.", "Consumer Cyclical"),
    "META": ("Meta Platforms Inc.", "Technology"),
    "NVDA": ("NVIDIA Corporation", "Technology"),
    "TSLA": ("Tesla Inc.", "Consumer Cyclical"),
    "NFLX": ("Netflix Inc.", "Communication Services"),
    "AMD": ("Advanced Micro Devices", "Technology"),
    "INTC": ("Intel Corporation", "Technology"),
    "CRM": ("Salesforce Inc.", "Technology"),
    "ORCL": ("Oracle Corporation", "Technology"),
    "IBM": ("International Business Machines", "Technology"),
    "CSCO": ("Cisco Systems Inc.", "Technology"),
    
    # Finance
    "JPM": ("JPMorgan Chase & Co.", "Financial Services"),
    "BAC": ("Bank of America Corp", "Financial Services"),
    "WFC": ("Wells Fargo & Company", "Financial Services"),
    "GS": ("Goldman Sachs Group Inc.", "Financial Services"),
    "MS": ("Morgan Stanley", "Financial Services"),
    "C": ("Citigroup Inc.", "Financial Services"),
    
    # Healthcare
    "JNJ": ("Johnson & Johnson", "Healthcare"),
    "UNH": ("UnitedHealth Group Inc.", "Healthcare"),
    "PFE": ("Pfizer Inc.", "Healthcare"),
    "ABBV": ("AbbVie Inc.", "Healthcare"),
    "MRK": ("Merck & Co. Inc.", "Healthcare"),
    "TMO": ("Thermo Fisher Scientific Inc.", "Healthcare"),
    
    # Consumer
    "WMT": ("Walmart Inc.", "Consumer Defensive"),
    "PG": ("Procter & Gamble Co.", "Consumer Defensive"),
    "KO": ("The Coca-Cola Company", "Consumer Defensive"),
    "PEP": ("PepsiCo Inc.", "Consumer Defensive"),
    "NKE": ("Nike Inc.", "Consumer Cyclical"),
    "SBUX": ("Starbucks Corporation", "Consumer Cyclical"),
    "MCD": ("McDonald's Corporation", "Consumer Cyclical"),
    
    # Industrial
    "BA": ("The Boeing Company", "Industrials"),
    "CAT": ("Caterpillar Inc.", "Industrials"),
    "GE": ("General Electric Company", "Industrials"),
    "HON": ("Honeywell International Inc.", "Industrials"),
    
    # Energy
    "XOM": ("Exxon Mobil Corporation", "Energy"),
    "CVX": ("Chevron Corporation", "Energy"),
    "COP": ("ConocoPhillips", "Energy"),
    
    # Communication
    "VZ": ("Verizon Communications Inc.", "Communication Services"),
    "T": ("AT&T Inc.", "Communication Services"),
    "DIS": ("The Walt Disney Company", "Communication Services"),
    "CMCSA": ("Comcast Corporation", "Communication Services"),
    
    # Other
    "V": ("Visa Inc.", "Financial Services"),
    "MA": ("Mastercard Incorporated", "Financial Services"),
    "HD": ("The Home Depot Inc.", "Consumer Cyclical"),
    "MRNA": ("Moderna Inc.", "Healthcare"),
    "PYPL": ("PayPal Holdings Inc.", "Financial Services"),
    "UBER": ("Uber Technologies Inc.", "Technology"),
    "LYFT": ("Lyft Inc.", "Technology"),
    "SPOT": ("Spotify Technology S.A.", "Communication Services"),
    "SQ": ("Block Inc.", "Technology"),
    "SHOP": ("Shopify Inc.", "Technology"),
    "ZM": ("Zoom Video Communications", "Technology"),
    "ROKU": ("Roku Inc.", "Communication Services"),
}


def search_stocks(query: str, limit: int = 20) -> list:
    """
    Search stocks by ticker or company name.
    
    Args:
        query: Search query (can be ticker or company name)
        limit: Maximum number of results to return
    
    Returns:
        List of dictionaries with ticker, name, and sector
    """
    if not query:
        return []
    
    query_upper = query.upper().strip()
    results = []
    
    # Exact ticker match (highest priority)
    if query_upper in POPULAR_STOCKS:
        name, sector = POPULAR_STOCKS[query_upper]
        results.append({
            "ticker": query_upper,
            "name": name,
            "sector": sector,
            "match_type": "ticker_exact"
        })
    
    # Ticker starts with query
    for ticker, (name, sector) in POPULAR_STOCKS.items():
        if ticker.startswith(query_upper) and ticker != query_upper:
            results.append({
                "ticker": ticker,
                "name": name,
                "sector": sector,
                "match_type": "ticker_prefix"
            })
    
    # Company name contains query (case-insensitive)
    query_lower = query.lower().strip()
    for ticker, (name, sector) in POPULAR_STOCKS.items():
        if query_lower in name.lower() and ticker not in [r["ticker"] for r in results]:
            results.append({
                "ticker": ticker,
                "name": name,
                "sector": sector,
                "match_type": "name_match"
            })
    
    # Sort by match type priority
    priority = {"ticker_exact": 0, "ticker_prefix": 1, "name_match": 2}
    results.sort(key=lambda x: (priority.get(x["match_type"], 3), x["ticker"]))
    
    return results[:limit]


def get_all_stocks() -> list:
    """
    Get all stocks in the database.
    
    Returns:
        List of all stocks with ticker, name, and sector
    """
    return [
        {
            "ticker": ticker,
            "name": name,
            "sector": sector
        }
        for ticker, (name, sector) in POPULAR_STOCKS.items()
    ]


def get_stock_display_name(ticker: str) -> str:
    """
    Get display name for a ticker (ticker - company name).
    
    Args:
        ticker: Stock ticker symbol
    
    Returns:
        Formatted display string
    """
    if ticker in POPULAR_STOCKS:
        name, sector = POPULAR_STOCKS[ticker]
        return f"{ticker} - {name}"
    return ticker

