from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict
import asyncio
from trading_engine import stock_analyzer

app = FastAPI(
    title="AI Stock Analyzer",
    description="Analyze a stock symbol using AI-powered agents (technical and sentiment)",
    version="2.0.0"
)

class AnalysisRequest(BaseModel):
    symbol: str

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
    try:
        result = await stock_analyzer.analyze(symbol)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 