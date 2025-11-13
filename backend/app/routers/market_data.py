"""
NSE/BSE Market Data API Router
Fetches live market prices for Indian stock exchanges
"""
from fastapi import APIRouter, HTTPException
import httpx
from typing import List, Dict, Any
import asyncio

router = APIRouter(prefix="/api/market", tags=["market"])

# Popular indices and stocks
INDICES = {
    "NIFTY 50": "^NSEI",
    "SENSEX": "^BSESN",
    "NIFTY BANK": "^NSEBANK",
    "NIFTY IT": "^CNXIT"
}

POPULAR_STOCKS = {
    "Reliance": "RELIANCE.NS",
    "TCS": "TCS.NS",
    "HDFC Bank": "HDFCBANK.NS",
    "Infosys": "INFY.NS",
    "ICICI Bank": "ICICIBANK.NS",
    "Bharti Airtel": "BHARTIARTL.NS",
    "ITC": "ITC.NS",
    "Kotak Bank": "KOTAKBANK.NS",
    "Axis Bank": "AXISBANK.NS",
    "HUL": "HINDUNILVR.NS"
}


async def fetch_stock_data(symbol: str, name: str) -> Dict[str, Any]:
    """Fetch stock data from Yahoo Finance via API"""
    try:
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}"
        params = {"interval": "1d", "range": "1d"}
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Accept": "application/json",
            "Accept-Language": "en-US,en;q=0.9"
        }
        
        # Add small delay to avoid rate limiting
        await asyncio.sleep(0.2)
        
        async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
            response = await client.get(url, params=params, headers=headers)
            
        if response.status_code != 200:
            print(f"Error fetching {symbol}: HTTP {response.status_code}")
            return None
            
        data = response.json()
        
        if "chart" not in data or "result" not in data["chart"]:
            print(f"Error fetching {symbol}: Invalid response structure")
            return None
        
        if not data["chart"]["result"] or len(data["chart"]["result"]) == 0:
            print(f"Error fetching {symbol}: No results in response")
            return None
            
        result = data["chart"]["result"][0]
        meta = result.get("meta", {})
        
        current_price = meta.get("regularMarketPrice", 0)
        previous_close = meta.get("previousClose", 0)
        
        if current_price and previous_close:
            change = current_price - previous_close
            change_percent = (change / previous_close) * 100
        else:
            change = 0
            change_percent = 0
        
        return {
            "name": name,
            "symbol": symbol,
            "price": round(current_price, 2) if current_price else 0,
            "change": round(change, 2),
            "changePercent": round(change_percent, 2),
            "previousClose": round(previous_close, 2) if previous_close else 0,
            "marketState": meta.get("marketState", "CLOSED")
        }
    except Exception as e:
        print(f"Error fetching {symbol}: {str(e)}")
        import traceback
        traceback.print_exc()
        return None


@router.get("/indices")
async def get_market_indices():
    """Get live prices for major Indian indices"""
    # Fetch indices one by one with delays to avoid rate limiting
    indices_data = []
    for name, symbol in INDICES.items():
        result = await fetch_stock_data(symbol, name)
        if result is not None:
            indices_data.append(result)
        await asyncio.sleep(0.3)  # 300ms delay between requests
    
    if not indices_data:
        raise HTTPException(status_code=503, detail="Unable to fetch market data. Please try again later.")
    
    return {"indices": indices_data}


@router.get("/stocks")
async def get_popular_stocks():
    """Get live prices for popular stocks"""
    # Fetch stocks one by one with delays to avoid rate limiting
    stocks_data = []
    for name, symbol in POPULAR_STOCKS.items():
        result = await fetch_stock_data(symbol, name)
        if result is not None:
            stocks_data.append(result)
        await asyncio.sleep(0.3)  # 300ms delay between requests
    
    if not stocks_data:
        raise HTTPException(status_code=503, detail="Unable to fetch stock data. Please try again later.")
    
    return {"stocks": stocks_data}


@router.get("/all")
async def get_all_market_data():
    """Get all market data (indices + stocks)"""
    # Fetch both indices and stocks concurrently
    indices_task = asyncio.create_task(get_market_indices())
    stocks_task = asyncio.create_task(get_popular_stocks())
    
    indices_result = await indices_task
    stocks_result = await stocks_task
    
    return {
        "indices": indices_result.get("indices", []),
        "stocks": stocks_result.get("stocks", [])
    }


@router.get("/search/{symbol}")
async def search_stock(symbol: str):
    """Search for a specific stock by symbol"""
    # Try NSE first
    nse_symbol = f"{symbol.upper()}.NS"
    result = await fetch_stock_data(nse_symbol, symbol.upper())
    
    if result:
        return result
    
    # Try BSE if NSE fails
    bse_symbol = f"{symbol.upper()}.BO"
    result = await fetch_stock_data(bse_symbol, symbol.upper())
    
    if result:
        return result
    
    raise HTTPException(status_code=404, detail=f"Stock {symbol} not found")

