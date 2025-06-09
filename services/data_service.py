import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import asyncio
import aiohttp
from config import config
import ta

class DataService:
    def __init__(self):
        self.session = None
    
    async def get_stock_data(self, symbol: str, period: str = "1d", interval: str = "1m") -> pd.DataFrame:
        """Get historical stock data from Yahoo Finance"""
        try:
            ticker = yf.Ticker(symbol)
            data = ticker.history(period=period, interval=interval)
            
            if data.empty:
                raise ValueError(f"No data found for symbol {symbol}")
            
            # Add technical indicators
            data = self.add_technical_indicators(data)
            return data
        except Exception as e:
            print(f"Error fetching data for {symbol}: {e}")
            return pd.DataFrame()
    
    def add_technical_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add technical indicators to the dataframe"""
        if df.empty:
            return df
        
        # Moving Averages
        df['SMA_20'] = ta.trend.sma_indicator(df['Close'], window=20)
        df['SMA_50'] = ta.trend.sma_indicator(df['Close'], window=50)
        df['EMA_12'] = ta.trend.ema_indicator(df['Close'], window=12)
        df['EMA_26'] = ta.trend.ema_indicator(df['Close'], window=26)
        
        # MACD
        df['MACD'] = ta.trend.macd(df['Close'])
        df['MACD_signal'] = ta.trend.macd_signal(df['Close'])
        df['MACD_histogram'] = ta.trend.macd_diff(df['Close'])
        
        # RSI
        df['RSI'] = ta.momentum.rsi(df['Close'], window=14)
        
        # Bollinger Bands
        bollinger = ta.volatility.BollingerBands(df['Close'])
        df['BB_upper'] = bollinger.bollinger_hband()
        df['BB_middle'] = bollinger.bollinger_mavg()
        df['BB_lower'] = bollinger.bollinger_lband()
        
        # Volume indicators
        df['Volume_SMA'] = ta.volume.volume_sma(df['Close'], df['Volume'], window=20)
        
        # Stochastic Oscillator
        df['Stoch_K'] = ta.momentum.stoch(df['High'], df['Low'], df['Close'])
        df['Stoch_D'] = ta.momentum.stoch_signal(df['High'], df['Low'], df['Close'])
        
        return df
    
    async def get_real_time_price(self, symbol: str) -> Dict:
        """Get real-time price data"""
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            
            return {
                'symbol': symbol,
                'price': info.get('regularMarketPrice', 0),
                'change': info.get('regularMarketChange', 0),
                'change_percent': info.get('regularMarketChangePercent', 0),
                'volume': info.get('regularMarketVolume', 0),
                'market_cap': info.get('marketCap', 0),
                'timestamp': datetime.now()
            }
        except Exception as e:
            print(f"Error fetching real-time data for {symbol}: {e}")
            return {}
    
    async def get_multiple_prices(self, symbols: List[str]) -> Dict[str, Dict]:
        """Get real-time prices for multiple symbols"""
        tasks = [self.get_real_time_price(symbol) for symbol in symbols]
        results = await asyncio.gather(*tasks)
        
        return {result['symbol']: result for result in results if result}
    
    async def get_stock_info(self, symbol: str) -> Dict:
        """Get detailed stock information"""
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            
            return {
                'symbol': symbol,
                'name': info.get('longName', ''),
                'sector': info.get('sector', ''),
                'industry': info.get('industry', ''),
                'market_cap': info.get('marketCap', 0),
                'pe_ratio': info.get('trailingPE', 0),
                'dividend_yield': info.get('dividendYield', 0),
                'beta': info.get('beta', 0),
                '52_week_high': info.get('fiftyTwoWeekHigh', 0),
                '52_week_low': info.get('fiftyTwoWeekLow', 0),
                'avg_volume': info.get('averageVolume', 0)
            }
        except Exception as e:
            print(f"Error fetching stock info for {symbol}: {e}")
            return {}
    
    def calculate_volatility(self, df: pd.DataFrame, window: int = 20) -> float:
        """Calculate historical volatility"""
        if df.empty or len(df) < window:
            return 0.0
        
        returns = df['Close'].pct_change().dropna()
        volatility = returns.rolling(window=window).std().iloc[-1]
        return volatility * np.sqrt(252)  # Annualized volatility
    
    def get_support_resistance_levels(self, df: pd.DataFrame) -> Dict[str, List[float]]:
        """Identify support and resistance levels"""
        if df.empty:
            return {'support': [], 'resistance': []}
        
        highs = df['High'].rolling(window=10, center=True).max()
        lows = df['Low'].rolling(window=10, center=True).min()
        
        resistance_levels = df[df['High'] == highs]['High'].unique()
        support_levels = df[df['Low'] == lows]['Low'].unique()
        
        return {
            'support': sorted(support_levels[-5:]) if len(support_levels) > 0 else [],
            'resistance': sorted(resistance_levels[-5:], reverse=True) if len(resistance_levels) > 0 else []
        }
    
    async def get_news_sentiment(self, symbol: str) -> Dict:
        """Get news and sentiment data (placeholder for now)"""
        # This would integrate with news APIs like Alpha Vantage, NewsAPI, etc.
        return {
            'sentiment_score': 0.0,
            'news_count': 0,
            'headlines': []
        }

# Global instance
data_service = DataService() 