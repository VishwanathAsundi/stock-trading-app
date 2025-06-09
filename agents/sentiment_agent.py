from .base_agent import BaseAgent, TradingSignal
import pandas as pd
from typing import Dict, List
import re

class SentimentAgent(BaseAgent):
    def __init__(self):
        super().__init__("Sentiment Analysis Agent")
        self.sentiment_keywords = {
            'positive': ['bullish', 'positive', 'growth', 'profit', 'revenue', 'strong', 'beat', 'exceed', 'upgrade'],
            'negative': ['bearish', 'negative', 'loss', 'decline', 'weak', 'miss', 'downgrade', 'concern', 'risk']
        }
    
    async def analyze(self, symbol: str, data: pd.DataFrame, market_data: Dict) -> TradingSignal:
        """Analyze market sentiment and generate trading signal"""
        current_price = data['Close'].iloc[-1] if not data.empty else market_data.get('price', 0)
        
        # Get news sentiment (placeholder - would integrate with news APIs)
        news_sentiment = await self._analyze_news_sentiment(symbol)
        
        # Analyze market sentiment indicators
        market_sentiment = self._analyze_market_sentiment(data, market_data)
        
        # Combine sentiment scores
        combined_sentiment = self._combine_sentiment_scores(news_sentiment, market_sentiment)
        
        # Determine action and confidence
        action, confidence = self._determine_action_from_sentiment(combined_sentiment)
        
        # Generate reasoning
        reasoning = self._generate_sentiment_reasoning(news_sentiment, market_sentiment, combined_sentiment)
        
        # Get AI-enhanced analysis
        ai_prompt = f"""
        Analyze market sentiment for {symbol}:
        Current Price: ${current_price:.2f}
        News Sentiment Score: {news_sentiment['score']:.2f}
        Market Sentiment Score: {market_sentiment['score']:.2f}
        Combined Sentiment: {combined_sentiment:.2f}
        
        Recent market conditions and any notable events affecting {symbol}.
        Provide sentiment-based trading recommendation and key factors to consider.
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
    
    async def _analyze_news_sentiment(self, symbol: str) -> Dict:
        """Analyze news sentiment for the stock"""
        # Placeholder implementation
        # In a real implementation, this would:
        # 1. Fetch recent news articles about the stock
        # 2. Use NLP to analyze sentiment
        # 3. Weight by source credibility and recency
        
        # Mock sentiment analysis
        import random
        
        sentiment_score = random.uniform(-1.0, 1.0)  # Mock sentiment
        news_count = random.randint(0, 20)
        
        return {
            'score': sentiment_score,
            'news_count': news_count,
            'confidence': min(news_count / 10.0, 1.0),  # More news = higher confidence
            'headlines': [
                f"Mock headline 1 for {symbol}",
                f"Mock headline 2 for {symbol}"
            ]
        }
    
    def _analyze_market_sentiment(self, data: pd.DataFrame, market_data: Dict) -> Dict:
        """Analyze market-based sentiment indicators"""
        if data.empty:
            return {'score': 0.0, 'confidence': 0.0, 'indicators': {}}
        
        indicators = {}
        
        # Volume analysis
        if 'Volume' in data.columns and 'Volume_SMA' in data.columns:
            current_volume = data['Volume'].iloc[-1]
            avg_volume = data['Volume_SMA'].iloc[-1]
            volume_ratio = current_volume / avg_volume if avg_volume > 0 else 1.0
            
            if volume_ratio > 1.5:
                indicators['volume'] = 0.3  # High volume positive
            elif volume_ratio < 0.5:
                indicators['volume'] = -0.2  # Low volume negative
            else:
                indicators['volume'] = 0.0
        
        # Price momentum
        if len(data) >= 5:
            recent_returns = data['Close'].pct_change().tail(5)
            momentum = recent_returns.mean()
            
            if momentum > 0.02:  # 2% average daily gain
                indicators['momentum'] = 0.4
            elif momentum < -0.02:  # 2% average daily loss
                indicators['momentum'] = -0.4
            else:
                indicators['momentum'] = momentum * 10  # Scale to -0.2 to 0.2
        
        # Volatility sentiment
        if len(data) >= 20:
            volatility = data['Close'].pct_change().rolling(20).std().iloc[-1]
            
            if volatility > 0.03:  # High volatility
                indicators['volatility'] = -0.2  # Generally negative
            elif volatility < 0.01:  # Low volatility
                indicators['volatility'] = 0.1  # Slightly positive
            else:
                indicators['volatility'] = 0.0
        
        # Calculate overall market sentiment
        sentiment_score = sum(indicators.values())
        confidence = len(indicators) / 3.0  # Max 3 indicators
        
        return {
            'score': max(-1.0, min(1.0, sentiment_score)),
            'confidence': confidence,
            'indicators': indicators
        }
    
    def _combine_sentiment_scores(self, news_sentiment: Dict, market_sentiment: Dict) -> float:
        """Combine news and market sentiment scores"""
        news_weight = 0.6
        market_weight = 0.4
        
        news_score = news_sentiment['score'] * news_sentiment['confidence']
        market_score = market_sentiment['score'] * market_sentiment['confidence']
        
        combined_score = (news_score * news_weight + market_score * market_weight)
        
        return max(-1.0, min(1.0, combined_score))
    
    def _determine_action_from_sentiment(self, sentiment_score: float) -> tuple[str, float]:
        """Determine trading action based on sentiment score"""
        abs_score = abs(sentiment_score)
        
        if sentiment_score > 0.3:
            return "buy", min(abs_score * 0.8, 0.9)  # Positive sentiment
        elif sentiment_score < -0.3:
            return "sell", min(abs_score * 0.8, 0.9)  # Negative sentiment
        else:
            return "hold", 0.2  # Neutral sentiment
    
    def _generate_sentiment_reasoning(self, news_sentiment: Dict, market_sentiment: Dict, combined_sentiment: float) -> str:
        """Generate human-readable reasoning for sentiment analysis"""
        reasoning_parts = []
        
        # News sentiment reasoning
        if news_sentiment['score'] > 0.2:
            reasoning_parts.append(f"Positive news sentiment ({news_sentiment['score']:.2f}) based on {news_sentiment['news_count']} articles")
        elif news_sentiment['score'] < -0.2:
            reasoning_parts.append(f"Negative news sentiment ({news_sentiment['score']:.2f}) based on {news_sentiment['news_count']} articles")
        else:
            reasoning_parts.append("Neutral news sentiment")
        
        # Market sentiment reasoning
        market_indicators = market_sentiment.get('indicators', {})
        
        if 'volume' in market_indicators:
            if market_indicators['volume'] > 0:
                reasoning_parts.append("High trading volume indicates strong interest")
            elif market_indicators['volume'] < 0:
                reasoning_parts.append("Low trading volume suggests weak interest")
        
        if 'momentum' in market_indicators:
            if market_indicators['momentum'] > 0.1:
                reasoning_parts.append("Strong positive price momentum")
            elif market_indicators['momentum'] < -0.1:
                reasoning_parts.append("Strong negative price momentum")
        
        if 'volatility' in market_indicators:
            if market_indicators['volatility'] < 0:
                reasoning_parts.append("High volatility suggests uncertainty")
        
        # Overall sentiment
        if combined_sentiment > 0.3:
            reasoning_parts.append("Overall sentiment is bullish")
        elif combined_sentiment < -0.3:
            reasoning_parts.append("Overall sentiment is bearish")
        else:
            reasoning_parts.append("Overall sentiment is neutral")
        
        return ". ".join(reasoning_parts) 