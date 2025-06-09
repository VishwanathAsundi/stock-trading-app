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
    # Try to resolve symbol if not a known ticker (e.g., if user entered "APPLE")
    if not (2 <= len(symbol) <= 5 and symbol.isalpha()):  # crude check, can be improved
        url = f"https://api.twelvedata.com/symbol_search?symbol={symbol}&apikey={TWELVE_DATA_API_KEY}"
        print("analyze url", url)
        try:
            r = requests.get(url, timeout=5)
            # r.raise_for_status()
            data = r.json()
            for item in data.get('data', []):
                if item.get('country') == 'United States' and item.get('exchange') in ['NYSE', 'NASDAQ']:
                    symbol = item['symbol']
                    break
        except Exception as e:
            print("twelvedata error", e)
            raise HTTPException(status_code=500, detail=str(e))
            
    try:
        result = await stock_analyzer.analyze(symbol)
        return result
    except Exception as e:
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
            # Only show US stocks (NYSE/NASDAQ)
            if item.get('country') == 'United States' and item.get('exchange') in ['NYSE', 'NASDAQ']:
                results.append({
                    "symbol": item['symbol'],
                    "shortname": item['instrument_name'],
                    "exchange": item['exchange'],
                    "type": item.get('instrument_type', '')
                })
        print("search results", results)
        return results
    except Exception as e:
        print("twelvedata error", e)
        return []