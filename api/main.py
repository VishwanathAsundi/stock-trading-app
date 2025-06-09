from fastapi import FastAPI, HTTPException, BackgroundTasks, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, List, Optional
import asyncio
from datetime import datetime

from trading_engine import trading_engine
from services.portfolio_service import portfolio_service
from services.data_service import data_service
from agents.risk_agent import RiskManagementAgent
from models.database import get_db, create_tables

# Initialize FastAPI app
app = FastAPI(
    title="AI Stock Trading Platform",
    description="Advanced AI-powered stock trading application with multiple intelligent agents",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize risk agent
risk_agent = RiskManagementAgent()

# Add risk agent to trading engine
trading_engine.agents['risk'] = risk_agent

# Pydantic models for API requests
class TradeRequest(BaseModel):
    symbol: str
    action: str  # 'buy' or 'sell'
    quantity: int
    strategy: str = "Manual"

class WatchlistRequest(BaseModel):
    symbol: str

class AnalysisRequest(BaseModel):
    symbol: str

# Startup event
@app.on_event("startup")
async def startup_event():
    """Initialize database and services on startup"""
    create_tables()
    print("🚀 Trading API Server Started!")

# Health check endpoint
@app.get("/")
async def root():
    return {
        "message": "AI Stock Trading Platform API",
        "version": "1.0.0",
        "status": "running",
        "trading_engine_status": "running" if trading_engine.is_running else "stopped"
    }

# Portfolio endpoints
@app.get("/api/portfolio")
async def get_portfolio():
    """Get current portfolio summary"""
    try:
        portfolio = await portfolio_service.get_portfolio_summary()
        return portfolio
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/portfolio/trades")
async def get_trade_history(limit: int = 50):
    """Get trade history"""
    try:
        trades = await portfolio_service.get_trade_history(limit=limit)
        return {"trades": trades}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/portfolio/position/{symbol}")
async def get_position(symbol: str):
    """Get position for a specific symbol"""
    try:
        position = await portfolio_service.get_position_by_symbol(symbol.upper())
        if position is None:
            return {"message": f"No position found for {symbol}"}
        return position
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Trading endpoints
@app.post("/api/trade")
async def execute_trade(trade_request: TradeRequest):
    """Execute a manual trade"""
    try:
        result = await portfolio_service.execute_trade(
            symbol=trade_request.symbol.upper(),
            action=trade_request.action.lower(),
            quantity=trade_request.quantity,
            strategy=trade_request.strategy,
            confidence=1.0  # Manual trades have full confidence
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# AI Analysis endpoints
@app.post("/api/analyze")
async def analyze_symbol(analysis_request: AnalysisRequest):
    """Get AI analysis for a specific symbol"""
    try:
        symbol = analysis_request.symbol.upper()
        analysis = await trading_engine.analyze_single_symbol(symbol)
        return analysis
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/agents/performance")
async def get_agent_performance():
    """Get performance metrics for all AI agents"""
    try:
        performance = trading_engine.get_agent_performance()
        return {"agents": performance}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Market data endpoints
@app.get("/api/market/{symbol}")
async def get_market_data(symbol: str, period: str = "1d", interval: str = "1h"):
    """Get market data for a symbol"""
    try:
        # Get price data
        price_data = await data_service.get_real_time_price(symbol.upper())
        
        # Get historical data
        historical_data = await data_service.get_stock_data(symbol.upper(), period, interval)
        
        # Get stock info
        stock_info = await data_service.get_stock_info(symbol.upper())
        
        # Convert DataFrame to dict for JSON serialization
        historical_dict = {}
        if not historical_data.empty:
            historical_dict = {
                'timestamps': historical_data.index.strftime('%Y-%m-%d %H:%M:%S').tolist(),
                'open': historical_data['Open'].tolist(),
                'high': historical_data['High'].tolist(),
                'low': historical_data['Low'].tolist(),
                'close': historical_data['Close'].tolist(),
                'volume': historical_data['Volume'].tolist()
            }
        
        return {
            "symbol": symbol.upper(),
            "current_price": price_data,
            "historical_data": historical_dict,
            "stock_info": stock_info
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/market/multiple")
async def get_multiple_market_data(symbols: str):
    """Get market data for multiple symbols (comma-separated)"""
    try:
        symbol_list = [s.strip().upper() for s in symbols.split(',')]
        market_data = await data_service.get_multiple_prices(symbol_list)
        return {"market_data": market_data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Trading engine control endpoints
@app.post("/api/trading/start")
async def start_trading(background_tasks: BackgroundTasks):
    """Start the automated trading engine"""
    if trading_engine.is_running:
        return {"message": "Trading engine is already running"}
    
    background_tasks.add_task(trading_engine.start_trading)
    return {"message": "Trading engine started"}

@app.post("/api/trading/stop")
async def stop_trading():
    """Stop the automated trading engine"""
    if not trading_engine.is_running:
        return {"message": "Trading engine is not running"}
    
    trading_engine.stop_trading()
    return {"message": "Trading engine stopped"}

@app.get("/api/trading/status")
async def get_trading_status():
    """Get trading engine status"""
    return {
        "is_running": trading_engine.is_running,
        "watchlist": trading_engine.watchlist,
        "agents": list(trading_engine.agents.keys()),
        "last_cycle": datetime.now().isoformat()
    }

# Watchlist endpoints
@app.get("/api/watchlist")
async def get_watchlist():
    """Get current watchlist"""
    return {"watchlist": trading_engine.watchlist}

@app.post("/api/watchlist/add")
async def add_to_watchlist(request: WatchlistRequest):
    """Add symbol to watchlist"""
    try:
        trading_engine.add_to_watchlist(request.symbol.upper())
        return {"message": f"Added {request.symbol.upper()} to watchlist"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/watchlist/remove/{symbol}")
async def remove_from_watchlist(symbol: str):
    """Remove symbol from watchlist"""
    try:
        trading_engine.remove_from_watchlist(symbol.upper())
        return {"message": f"Removed {symbol.upper()} from watchlist"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Risk analysis endpoints
@app.post("/api/risk/analyze")
async def analyze_risk(analysis_request: AnalysisRequest):
    """Get risk analysis for a specific symbol"""
    try:
        symbol = analysis_request.symbol.upper()
        
        # Get market data
        data = await data_service.get_stock_data(symbol, period="5d", interval="1h")
        market_data = await data_service.get_real_time_price(symbol)
        
        if data.empty or not market_data:
            raise HTTPException(status_code=404, detail=f"No data available for {symbol}")
        
        # Get risk analysis
        risk_signal = await risk_agent.analyze(symbol, data, market_data)
        
        return {
            "symbol": symbol,
            "risk_analysis": {
                "action": risk_signal.action,
                "confidence": risk_signal.confidence,
                "reasoning": risk_signal.reasoning,
                "position_size": risk_signal.position_size,
                "stop_loss": risk_signal.stop_loss,
                "target_price": risk_signal.target_price
            },
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Dashboard data endpoint
@app.get("/api/dashboard")
async def get_dashboard_data():
    """Get comprehensive dashboard data"""
    try:
        # Get portfolio summary
        portfolio = await portfolio_service.get_portfolio_summary()
        
        # Get recent trades
        recent_trades = await portfolio_service.get_trade_history(limit=10)
        
        # Get agent performance
        agent_performance = trading_engine.get_agent_performance()
        
        # Get watchlist with current prices
        watchlist_data = []
        for symbol in trading_engine.watchlist[:5]:  # Limit to 5 for dashboard
            try:
                price_data = await data_service.get_real_time_price(symbol)
                watchlist_data.append({
                    "symbol": symbol,
                    "price": price_data.get('price', 0),
                    "change_percent": price_data.get('change_percent', 0)
                })
            except:
                continue
        
        return {
            "portfolio": portfolio,
            "recent_trades": recent_trades,
            "agent_performance": agent_performance,
            "watchlist": watchlist_data,
            "trading_engine_status": trading_engine.is_running,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True) 