import asyncio
from typing import Dict
from agents.technical_agent import TechnicalAgent
from agents.sentiment_agent import SentimentAgent
from agents.base_agent import TradingSignal
from services.data_service import data_service, map_symbol_for_yfinance
from config import config

class StockAnalyzer:
    def __init__(self):
        self.agents = {
            'technical': TechnicalAgent(),
            'sentiment': SentimentAgent(),
        }

    async def analyze(self, symbol: str, exchange: str = None) -> Dict:
        """Analyze a single symbol and return signals and consensus"""
        # Map symbol for yfinance if exchange is provided
        yf_symbol = symbol
        if exchange:
            yf_symbol = map_symbol_for_yfinance(symbol, exchange)
        # Determine currency
        currency = '₹' if exchange in ['NSE', 'BSE'] else '$'
        # Get market data
        data = await data_service.get_stock_data(yf_symbol, period="5d", interval="1h")
        market_data = await data_service.get_real_time_price(yf_symbol)
        if data.empty or not market_data:
            return {"error": f"No data available for {symbol}"}
        # Get signals from all agents
        signals = {}
        for agent_name, agent in self.agents.items():
            try:
                signal = await agent.analyze(yf_symbol, data, market_data)
                signals[agent_name] = {
                    'action': signal.action,
                    'confidence': signal.confidence,
                    'reasoning': signal.reasoning,
                    'target_price': signal.target_price,
                    'stop_loss': signal.stop_loss
                }
            except Exception as e:
                signals[agent_name] = {'error': str(e)}
        # Calculate consensus
        valid_signals = {k: v for k, v in signals.items() if 'error' not in v}
        if valid_signals:
            # Convert back to TradingSignal objects for consensus calculation
            signal_objects = {}
            for name, sig_data in valid_signals.items():
                signal_objects[name] = TradingSignal(
                    symbol=yf_symbol,
                    action=sig_data['action'],
                    confidence=sig_data['confidence'],
                    reasoning=sig_data['reasoning'],
                    target_price=sig_data.get('target_price'),
                    stop_loss=sig_data.get('stop_loss')
                )
            consensus = self._calculate_consensus(signal_objects)
        else:
            consensus = {'action': 'hold', 'confidence': 0.0, 'agreement': 0.0}
        return {
            'symbol': yf_symbol,
            'current_price': market_data.get('price', 0),
            'currency': currency,
            'signals': signals,
            'consensus': consensus
        }

    def _calculate_consensus(self, signals: Dict[str, TradingSignal]) -> Dict:
        """Calculate consensus from multiple agent signals"""
        if not signals:
            return {'action': 'hold', 'confidence': 0.0, 'agreement': 0.0}
        agent_weights = {
            'technical': 0.5,
            'sentiment': 0.5
        }
        buy_score = 0.0
        sell_score = 0.0
        hold_score = 0.0
        total_weight = 0.0
        actions = []
        confidences = []
        for agent_name, signal in signals.items():
            weight = agent_weights.get(agent_name, 0.5)
            confidence = signal.confidence
            if signal.action == 'buy':
                buy_score += weight * confidence
            elif signal.action == 'sell':
                sell_score += weight * confidence
            else:
                hold_score += weight * confidence
            total_weight += weight
            actions.append(signal.action)
            confidences.append(confidence)
        if total_weight > 0:
            buy_score /= total_weight
            sell_score /= total_weight
            hold_score /= total_weight
        if buy_score > sell_score and buy_score > hold_score:
            consensus_action = 'buy'
            consensus_confidence = buy_score
        elif sell_score > buy_score and sell_score > hold_score:
            consensus_action = 'sell'
            consensus_confidence = sell_score
        else:
            consensus_action = 'hold'
            consensus_confidence = hold_score
        most_common_action = max(set(actions), key=actions.count)
        agreement = actions.count(most_common_action) / len(actions)
        return {
            'action': consensus_action,
            'confidence': consensus_confidence,
            'agreement': agreement,
            'buy_score': buy_score,
            'sell_score': sell_score,
            'hold_score': hold_score
        }

stock_analyzer = StockAnalyzer() 