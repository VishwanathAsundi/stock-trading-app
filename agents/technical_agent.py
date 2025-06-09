from .base_agent import BaseAgent, TradingSignal
import pandas as pd
from typing import Dict
import numpy as np

class TechnicalAgent(BaseAgent):
    def __init__(self):
        super().__init__("Technical Analysis Agent")
        self.min_data_points = 50
    
    async def analyze(self, symbol: str, data: pd.DataFrame, market_data: Dict) -> TradingSignal:
        """Analyze technical indicators and generate trading signal"""
        if data.empty or len(data) < self.min_data_points:
            return TradingSignal(
                symbol=symbol,
                action="hold",
                confidence=0.0,
                reasoning="Insufficient data for technical analysis"
            )
        
        current_price = data['Close'].iloc[-1]
        
        # Calculate technical signals
        signals = self._calculate_technical_signals(data)
        
        # Weight the signals
        weighted_score = self._calculate_weighted_score(signals)
        
        # Determine action and confidence
        action, confidence = self._determine_action(weighted_score)
        
        # Generate reasoning
        reasoning = self._generate_reasoning(signals, current_price)
        
        # Get AI-enhanced analysis
        ai_prompt = f"""
        Analyze {symbol} technical indicators:
        Current Price: ${current_price:.2f}
        RSI: {data['RSI'].iloc[-1]:.2f}
        MACD: {data['MACD'].iloc[-1]:.4f}
        Signal: {data['MACD_signal'].iloc[-1]:.4f}
        SMA 20: ${data['SMA_20'].iloc[-1]:.2f}
        SMA 50: ${data['SMA_50'].iloc[-1]:.2f}
        
        Technical Score: {weighted_score:.2f}
        Suggested Action: {action}
        
        Provide a brief technical analysis and confirm or adjust the trading recommendation.
        """
        
        ai_analysis = await self._get_ai_analysis(ai_prompt)
        
        signal = TradingSignal(
            symbol=symbol,
            action=action,
            confidence=confidence,
            reasoning=f"{reasoning}\n\nAI Analysis: {ai_analysis}",
            target_price=self._calculate_take_profit(current_price, action),
            stop_loss=self._calculate_stop_loss(current_price, action),
            position_size=self._calculate_position_size(confidence, 100000)
        )
        
        self.record_signal(signal)
        return signal
    
    def _calculate_technical_signals(self, data: pd.DataFrame) -> Dict[str, float]:
        """Calculate various technical signals"""
        latest = data.iloc[-1]
        prev = data.iloc[-2] if len(data) > 1 else latest
        
        signals = {}
        
        # RSI Signal
        rsi = latest['RSI']
        if rsi < 30:
            signals['rsi'] = 1.0  # Oversold - buy signal
        elif rsi > 70:
            signals['rsi'] = -1.0  # Overbought - sell signal
        else:
            signals['rsi'] = 0.0  # Neutral
        
        # MACD Signal
        macd = latest['MACD']
        macd_signal = latest['MACD_signal']
        macd_prev = prev['MACD']
        macd_signal_prev = prev['MACD_signal']
        
        if macd > macd_signal and macd_prev <= macd_signal_prev:
            signals['macd'] = 1.0  # Bullish crossover
        elif macd < macd_signal and macd_prev >= macd_signal_prev:
            signals['macd'] = -1.0  # Bearish crossover
        else:
            signals['macd'] = 0.0  # No clear signal
        
        # Moving Average Signal
        price = latest['Close']
        sma_20 = latest['SMA_20']
        sma_50 = latest['SMA_50']
        
        if price > sma_20 > sma_50:
            signals['ma'] = 1.0  # Bullish trend
        elif price < sma_20 < sma_50:
            signals['ma'] = -1.0  # Bearish trend
        else:
            signals['ma'] = 0.0  # Sideways
        
        # Bollinger Bands Signal
        bb_upper = latest['BB_upper']
        bb_lower = latest['BB_lower']
        
        if price <= bb_lower:
            signals['bb'] = 1.0  # Oversold
        elif price >= bb_upper:
            signals['bb'] = -1.0  # Overbought
        else:
            signals['bb'] = 0.0  # Within bands
        
        # Stochastic Signal
        stoch_k = latest['Stoch_K']
        stoch_d = latest['Stoch_D']
        
        if stoch_k < 20 and stoch_d < 20:
            signals['stoch'] = 1.0  # Oversold
        elif stoch_k > 80 and stoch_d > 80:
            signals['stoch'] = -1.0  # Overbought
        else:
            signals['stoch'] = 0.0  # Neutral
        
        # Volume Signal
        volume = latest['Volume']
        volume_sma = latest['Volume_SMA']
        
        if volume > volume_sma * 1.5:
            # High volume - amplify other signals
            signals['volume_multiplier'] = 1.2
        else:
            signals['volume_multiplier'] = 1.0
        
        return signals
    
    def _calculate_weighted_score(self, signals: Dict[str, float]) -> float:
        """Calculate weighted technical score"""
        weights = {
            'rsi': 0.2,
            'macd': 0.25,
            'ma': 0.25,
            'bb': 0.15,
            'stoch': 0.15
        }
        
        score = 0.0
        for indicator, weight in weights.items():
            if indicator in signals:
                score += signals[indicator] * weight
        
        # Apply volume multiplier
        score *= signals.get('volume_multiplier', 1.0)
        
        return score
    
    def _determine_action(self, score: float) -> tuple[str, float]:
        """Determine action and confidence based on score"""
        abs_score = abs(score)
        
        if score > 0.3:
            return "buy", min(abs_score, 0.9)
        elif score < -0.3:
            return "sell", min(abs_score, 0.9)
        else:
            return "hold", 0.1
    
    def _generate_reasoning(self, signals: Dict[str, float], current_price: float) -> str:
        """Generate human-readable reasoning"""
        reasoning_parts = []
        
        if signals.get('rsi', 0) > 0:
            reasoning_parts.append("RSI indicates oversold conditions")
        elif signals.get('rsi', 0) < 0:
            reasoning_parts.append("RSI indicates overbought conditions")
        
        if signals.get('macd', 0) > 0:
            reasoning_parts.append("MACD bullish crossover detected")
        elif signals.get('macd', 0) < 0:
            reasoning_parts.append("MACD bearish crossover detected")
        
        if signals.get('ma', 0) > 0:
            reasoning_parts.append("Price above moving averages - bullish trend")
        elif signals.get('ma', 0) < 0:
            reasoning_parts.append("Price below moving averages - bearish trend")
        
        if signals.get('bb', 0) > 0:
            reasoning_parts.append("Price at lower Bollinger Band - potential bounce")
        elif signals.get('bb', 0) < 0:
            reasoning_parts.append("Price at upper Bollinger Band - potential reversal")
        
        if signals.get('volume_multiplier', 1.0) > 1.0:
            reasoning_parts.append("High volume confirms the signal")
        
        return ". ".join(reasoning_parts) if reasoning_parts else "Mixed technical signals" 