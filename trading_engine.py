import asyncio
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import pandas as pd

from agents.technical_agent import TechnicalAgent
from agents.sentiment_agent import SentimentAgent
from agents.base_agent import TradingSignal
from services.data_service import data_service
from services.portfolio_service import portfolio_service
from models.database import create_tables, AISignal, get_db
from config import config
import json

class TradingEngine:
    def __init__(self):
        self.agents = {
            'technical': TechnicalAgent(),
            'sentiment': SentimentAgent(),
        }
        self.watchlist = ['AAPL', 'GOOGL', 'MSFT', 'TSLA', 'AMZN', 'NVDA', 'META', 'NFLX']
        self.is_running = False
        self.last_analysis_time = {}
        
        # Initialize database
        create_tables()
    
    async def start_trading(self):
        """Start the automated trading engine"""
        self.is_running = True
        print("🚀 Trading Engine Started!")
        print(f"📊 Monitoring {len(self.watchlist)} symbols")
        print(f"🤖 Active agents: {list(self.agents.keys())}")
        
        while self.is_running:
            try:
                await self._trading_cycle()
                await asyncio.sleep(config.AI_UPDATE_INTERVAL)  # Wait 5 minutes
            except Exception as e:
                print(f"❌ Error in trading cycle: {e}")
                await asyncio.sleep(60)  # Wait 1 minute before retrying
    
    def stop_trading(self):
        """Stop the trading engine"""
        self.is_running = False
        print("🛑 Trading Engine Stopped!")
    
    async def _trading_cycle(self):
        """Execute one complete trading cycle"""
        print(f"\n📈 Starting trading cycle at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Analyze each symbol in the watchlist
        for symbol in self.watchlist:
            try:
                await self._analyze_symbol(symbol)
            except Exception as e:
                print(f"❌ Error analyzing {symbol}: {e}")
        
        print("✅ Trading cycle completed")
    
    async def _analyze_symbol(self, symbol: str):
        """Analyze a single symbol with all agents"""
        print(f"\n🔍 Analyzing {symbol}...")
        
        # Get market data
        data = await data_service.get_stock_data(symbol, period="5d", interval="1h")
        market_data = await data_service.get_real_time_price(symbol)
        
        if data.empty or not market_data:
            print(f"⚠️ No data available for {symbol}")
            return
        
        # Get signals from all agents
        signals = {}
        for agent_name, agent in self.agents.items():
            try:
                signal = await agent.analyze(symbol, data, market_data)
                signals[agent_name] = signal
                
                # Store signal in database
                await self._store_signal(signal, agent_name)
                
                print(f"🤖 {agent_name}: {signal.action.upper()} (confidence: {signal.confidence:.2f})")
            except Exception as e:
                print(f"❌ Error with {agent_name} agent for {symbol}: {e}")
        
        # Make trading decision
        if signals:
            await self._make_trading_decision(symbol, signals, market_data)
    
    async def _store_signal(self, signal: TradingSignal, agent_name: str):
        """Store AI signal in database"""
        try:
            db = next(get_db())
            
            ai_signal = AISignal(
                symbol=signal.symbol,
                agent_name=agent_name,
                signal_type=signal.action,
                confidence_score=signal.confidence,
                reasoning=signal.reasoning,
                technical_indicators=json.dumps({}),  # Could store more detailed indicators
                sentiment_score=0.0 if agent_name != 'sentiment' else signal.confidence
            )
            
            db.add(ai_signal)
            db.commit()
            db.close()
        except Exception as e:
            print(f"⚠️ Failed to store signal: {e}")
    
    async def _make_trading_decision(self, symbol: str, signals: Dict[str, TradingSignal], market_data: Dict):
        """Make final trading decision based on all agent signals"""
        current_price = market_data.get('price', 0)
        
        # Calculate consensus
        consensus = self._calculate_consensus(signals)
        
        print(f"📊 Consensus for {symbol}:")
        print(f"   Action: {consensus['action']}")
        print(f"   Confidence: {consensus['confidence']:.2f}")
        print(f"   Agreement: {consensus['agreement']:.2f}")
        
        # Only execute trades with high confidence and agreement
        if (consensus['confidence'] >= 0.6 and 
            consensus['agreement'] >= 0.7 and 
            consensus['action'] in ['buy', 'sell']):
            
            await self._execute_consensus_trade(symbol, consensus, current_price)
        else:
            print(f"⏸️ No trade executed for {symbol} - insufficient consensus")
    
    def _calculate_consensus(self, signals: Dict[str, TradingSignal]) -> Dict:
        """Calculate consensus from multiple agent signals"""
        if not signals:
            return {'action': 'hold', 'confidence': 0.0, 'agreement': 0.0}
        
        # Weight different agents
        agent_weights = {
            'technical': 0.4,
            'sentiment': 0.3,
            'risk': 0.3  # Will be added later
        }
        
        # Calculate weighted scores
        buy_score = 0.0
        sell_score = 0.0
        hold_score = 0.0
        total_weight = 0.0
        
        actions = []
        confidences = []
        
        for agent_name, signal in signals.items():
            weight = agent_weights.get(agent_name, 0.2)
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
        
        # Normalize scores
        if total_weight > 0:
            buy_score /= total_weight
            sell_score /= total_weight
            hold_score /= total_weight
        
        # Determine consensus action
        if buy_score > sell_score and buy_score > hold_score:
            consensus_action = 'buy'
            consensus_confidence = buy_score
        elif sell_score > buy_score and sell_score > hold_score:
            consensus_action = 'sell'
            consensus_confidence = sell_score
        else:
            consensus_action = 'hold'
            consensus_confidence = hold_score
        
        # Calculate agreement (how much agents agree)
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
    
    async def _execute_consensus_trade(self, symbol: str, consensus: Dict, current_price: float):
        """Execute trade based on consensus decision"""
        action = consensus['action']
        confidence = consensus['confidence']
        
        # Calculate position size based on confidence and current portfolio
        portfolio_summary = await portfolio_service.get_portfolio_summary()
        portfolio_value = portfolio_summary['total_value']
        
        # Check if we already have a position
        current_position = await portfolio_service.get_position_by_symbol(symbol)
        
        # Position sizing logic
        target_position_value = portfolio_value * confidence * 0.1  # Max 10% per position
        quantity = int(target_position_value / current_price)
        
        # Risk management checks
        if action == 'buy':
            if current_position:
                print(f"⚠️ Already have position in {symbol}, skipping buy")
                return
            
            if quantity < 1:
                print(f"⚠️ Position size too small for {symbol}")
                return
            
            # Check cash balance
            if portfolio_summary['cash_balance'] < quantity * current_price:
                print(f"⚠️ Insufficient cash for {symbol} trade")
                return
        
        elif action == 'sell':
            if not current_position or current_position['quantity'] <= 0:
                print(f"⚠️ No position to sell for {symbol}")
                return
            
            # Sell the entire position
            quantity = current_position['quantity']
        
        # Execute the trade
        print(f"🔄 Executing {action.upper()} order for {symbol}")
        print(f"   Quantity: {quantity}")
        print(f"   Price: ${current_price:.2f}")
        print(f"   Total: ${quantity * current_price:.2f}")
        
        result = await portfolio_service.execute_trade(
            symbol=symbol,
            action=action,
            quantity=quantity,
            strategy=f"AI Consensus ({consensus['agreement']:.1%} agreement)",
            confidence=confidence
        )
        
        if result.get('success'):
            print(f"✅ Trade executed successfully - ID: {result['trade_id']}")
        else:
            print(f"❌ Trade failed: {result.get('error', 'Unknown error')}")
    
    async def analyze_single_symbol(self, symbol: str) -> Dict:
        """Analyze a single symbol and return signals (for API/UI)"""
        # Get market data
        data = await data_service.get_stock_data(symbol, period="5d", interval="1h")
        market_data = await data_service.get_real_time_price(symbol)
        
        if data.empty or not market_data:
            return {"error": f"No data available for {symbol}"}
        
        # Get signals from all agents
        signals = {}
        for agent_name, agent in self.agents.items():
            try:
                signal = await agent.analyze(symbol, data, market_data)
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
                    symbol=symbol,
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
            'symbol': symbol,
            'current_price': market_data.get('price', 0),
            'signals': signals,
            'consensus': consensus,
            'timestamp': datetime.now().isoformat()
        }
    
    def get_agent_performance(self) -> Dict:
        """Get performance metrics for all agents"""
        performance = {}
        for agent_name, agent in self.agents.items():
            performance[agent_name] = agent.get_performance_metrics()
        return performance
    
    def add_to_watchlist(self, symbol: str):
        """Add symbol to watchlist"""
        if symbol not in self.watchlist:
            self.watchlist.append(symbol.upper())
            print(f"📌 Added {symbol} to watchlist")
    
    def remove_from_watchlist(self, symbol: str):
        """Remove symbol from watchlist"""
        if symbol in self.watchlist:
            self.watchlist.remove(symbol)
            print(f"🗑️ Removed {symbol} from watchlist")

# Global trading engine instance
trading_engine = TradingEngine() 