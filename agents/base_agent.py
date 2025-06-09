from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Tuple
import pandas as pd
from dataclasses import dataclass
from datetime import datetime
from openai import OpenAI
from config import config

@dataclass
class TradingSignal:
    symbol: str
    action: str  # 'buy', 'sell', 'hold'
    confidence: float  # 0.0 to 1.0
    reasoning: str
    target_price: Optional[float] = None
    stop_loss: Optional[float] = None
    position_size: Optional[float] = None
    timestamp: datetime = datetime.now()

class BaseAgent(ABC):
    def __init__(self, name: str):
        self.name = name
        self.client = OpenAI(api_key=config.OPENAI_API_KEY) if config.OPENAI_API_KEY else None
        self.signals_history: List[TradingSignal] = []
    
    @abstractmethod
    async def analyze(self, symbol: str, data: pd.DataFrame, market_data: Dict) -> TradingSignal:
        """Analyze market data and generate trading signal"""
        pass
    
    def _calculate_position_size(self, confidence: float, portfolio_value: float) -> float:
        """Calculate position size based on confidence and risk management"""
        base_size = config.MAX_POSITION_SIZE
        
        # Adjust position size based on confidence
        adjusted_size = base_size * confidence
        
        # Apply risk tolerance
        if config.RISK_TOLERANCE == "low":
            adjusted_size *= 0.5
        elif config.RISK_TOLERANCE == "high":
            adjusted_size *= 1.5
        
        return min(adjusted_size, 0.2)  # Cap at 20% of portfolio
    
    def _calculate_stop_loss(self, current_price: float, action: str) -> float:
        """Calculate stop loss price"""
        if action == "buy":
            return current_price * (1 - config.STOP_LOSS_PERCENTAGE)
        elif action == "sell":
            return current_price * (1 + config.STOP_LOSS_PERCENTAGE)
        return current_price
    
    def _calculate_take_profit(self, current_price: float, action: str) -> float:
        """Calculate take profit price"""
        if action == "buy":
            return current_price * (1 + config.TAKE_PROFIT_PERCENTAGE)
        elif action == "sell":
            return current_price * (1 - config.TAKE_PROFIT_PERCENTAGE)
        return current_price
    
    async def _get_ai_analysis(self, prompt: str) -> str:
        """Get analysis from OpenAI"""
        if not self.client:
            return "AI analysis unavailable - no OpenAI API key"
        
        try:
            response = await self.client.chat.completions.acreate(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a professional stock trading analyst."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=500,
                temperature=0.7
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"AI analysis error: {str(e)}"
    
    def record_signal(self, signal: TradingSignal):
        """Record a trading signal"""
        self.signals_history.append(signal)
        # Keep only last 100 signals
        if len(self.signals_history) > 100:
            self.signals_history = self.signals_history[-100:]
    
    def get_performance_metrics(self) -> Dict:
        """Get performance metrics for this agent"""
        if not self.signals_history:
            return {"total_signals": 0, "accuracy": 0.0, "avg_confidence": 0.0}
        
        total_signals = len(self.signals_history)
        avg_confidence = sum(s.confidence for s in self.signals_history) / total_signals
        
        return {
            "total_signals": total_signals,
            "avg_confidence": avg_confidence,
            "buy_signals": len([s for s in self.signals_history if s.action == "buy"]),
            "sell_signals": len([s for s in self.signals_history if s.action == "sell"]),
            "hold_signals": len([s for s in self.signals_history if s.action == "hold"])
        } 