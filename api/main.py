from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
from typing import Dict
import asyncio
from trading_engine import stock_analyzer
import requests
from fastapi.middleware.cors import CORSMiddleware
import os

app = FastAPI(
    title="AI Stock Analyzer",
    description="Analyze a stock symbol using AI-powered agents (technical and sentiment)",
    version="2.0.0"
)

# Add CORS middleware
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

class AnalysisRequest(BaseModel):
    symbol: str

TWELVE_DATA_API_KEY = os.getenv("TWELVE_DATA_API_KEY", "")

@app.get("/")
def root():
    return {
        "message": "AI Stock Analyzer API",
        "version": "2.0.0",
        "status": "running"
    }

@app.post("/analyze")
async def analyze_symbol(request: AnalysisRequest):
    symbol = request.symbol.upper()
    print("analyze symbol", symbol)
    exchange = None
    # Try to resolve symbol if not a known ticker (e.g., if user entered "APPLE")
    if not (2 <= len(symbol) <= 5 and symbol.isalpha()):  # crude check, can be improved
        url = f"https://api.twelvedata.com/symbol_search?symbol={symbol.upper()}&apikey={TWELVE_DATA_API_KEY}"
        print("analyze url", url)
        try:
            r = requests.get(url, timeout=5)
            # r.raise_for_status()
            data = r.json()
            print("analyze data", data)
            for item in data.get('data', []):
                if item.get('exchange') in ['NYSE', 'NASDAQ', 'NSE', 'BSE']:
                    symbol = item['symbol']
                    exchange = item['exchange']
                    break
        except Exception as e:
            print("twelvedata error", e, end="\n\n")
            raise HTTPException(status_code=500, detail=str(e))
    
    try:
        result = await stock_analyzer.analyze(symbol, exchange)
        return result
    except Exception as e:
        print("analyze error", e, end="\n\n")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/search")
def search_companies(q: str = Query(..., min_length=1)):
    url = f"https://api.twelvedata.com/symbol_search?symbol={q}&apikey={TWELVE_DATA_API_KEY}"
    print("search url", url)
    try:
        r = requests.get(url, timeout=5)
        print("search response", r.json())
        # r.raise_for_status()
        data = r.json()
        results = []
        for item in data.get('data', []):
            # Support US and Indian stocks (NYSE, NASDAQ, NSE, BSE)
            if item.get('exchange') in ['NYSE', 'NASDAQ', 'NSE', 'BSE']:
                results.append({
                    "symbol": item['symbol'],
                    "shortname": item.get('instrument_name', item.get('name', '')),
                    "exchange": item['exchange'],
                    "type": item.get('instrument_type', '')
                })
        print("search results", results)
        return results
    except Exception as e:
        print("twelvedata error", e)
        return []