from abc import ABC, abstractmethod
from typing import Dict, List, Optional
import pandas as pd
from dataclasses import dataclass
from config import config
import time

@dataclass
class TradingSignal:
    symbol: str
    action: str  # 'buy', 'sell', 'hold'
    confidence: float  # 0.0 to 1.0
    reasoning: str
    target_price: Optional[float] = None
    stop_loss: Optional[float] = None
    position_size: Optional[float] = None

class BaseAgent(ABC):
    def __init__(self, name: str):
        self.name = name
        self.signals_generated = 0
        self.total_confidence = 0.0
        self.performance_history = []
    
    @abstractmethod
    async def analyze(self, symbol: str, data: pd.DataFrame, market_data: Dict) -> TradingSignal:
        """Analyze market data and generate trading signal"""
        pass
    
    def record_signal(self, signal: TradingSignal):
        """Record signal for performance tracking"""
        self.signals_generated += 1
        self.total_confidence += signal.confidence
        self.performance_history.append({
            'timestamp': time.time(),
            'symbol': signal.symbol,
            'action': signal.action,
            'confidence': signal.confidence
        })
        
        # Keep only last 100 signals
        if len(self.performance_history) > 100:
            self.performance_history = self.performance_history[-100:]
    
    def get_performance_metrics(self) -> Dict:
        """Get performance metrics for this agent"""
        return {
            'total_signals': self.signals_generated,
            'avg_confidence': self.total_confidence / max(1, self.signals_generated),
            'recent_signals': len(self.performance_history),
            'last_signal_time': self.performance_history[-1]['timestamp'] if self.performance_history else None
        }
    
    async def _get_ai_analysis(self, prompt: str) -> str:
        """Get AI analysis using OpenAI (optional, requires API key)"""
        try:
            if hasattr(config, 'OPENAI_API_KEY') and config.OPENAI_API_KEY and config.OPENAI_API_KEY != 'your_openai_api_key_here':
                from openai import OpenAI
                client = OpenAI(api_key=config.OPENAI_API_KEY)
                
                response = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "You are a financial analyst. Provide concise, factual analysis."},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=150,
                    temperature=0.7
                )
                return response.choices[0].message.content.strip()
            else:
                return "AI analysis not available (API key not configured)"
        except Exception as e:
            return f"AI analysis error: {str(e)}"
    
    def _calculate_position_size(self, confidence: float, portfolio_value: float) -> float:
        """Calculate position size based on confidence and risk tolerance"""
        base_size = portfolio_value * config.MAX_POSITION_SIZE
        risk_adjusted_size = base_size * confidence
        return risk_adjusted_size
    
    def _calculate_stop_loss(self, current_price: float, action: str) -> float:
        """Calculate stop loss price"""
        if action == 'buy':
            return current_price * (1 - config.STOP_LOSS_PERCENTAGE)
        elif action == 'sell':
            return current_price * (1 + config.STOP_LOSS_PERCENTAGE)
        return current_price
    
    def _calculate_take_profit(self, current_price: float, action: str) -> float:
        """Calculate take profit price"""
        if action == 'buy':
            return current_price * (1 + config.TAKE_PROFIT_PERCENTAGE)
        elif action == 'sell':
            return current_price * (1 - config.TAKE_PROFIT_PERCENTAGE)
        return current_price 