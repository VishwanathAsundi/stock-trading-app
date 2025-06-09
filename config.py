import os
from dotenv import load_dotenv
from typing import Literal

load_dotenv()

class Config:
    # API Keys
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
    ALPHA_VANTAGE_API_KEY = os.getenv("ALPHA_VANTAGE_API_KEY", "")
    
    # Database
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./trading_app.db")
    REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
    
    # Security
    SECRET_KEY = os.getenv("SECRET_KEY", "default-secret-key-change-in-production")
    
    # Trading Configuration
    RISK_TOLERANCE: Literal["low", "medium", "high"] = os.getenv("RISK_TOLERANCE", "medium")
    MAX_POSITION_SIZE = float(os.getenv("MAX_POSITION_SIZE", "0.1"))
    TRADING_MODE: Literal["paper", "live"] = os.getenv("TRADING_MODE", "paper")
    
    # Portfolio Settings
    INITIAL_BALANCE = 100000.0  # $100k for paper trading
    MAX_POSITIONS = 10
    STOP_LOSS_PERCENTAGE = 0.05  # 5%
    TAKE_PROFIT_PERCENTAGE = 0.15  # 15%
    
    # AI Agent Settings
    AI_UPDATE_INTERVAL = 300  # 5 minutes
    SENTIMENT_ANALYSIS_ENABLED = True
    TECHNICAL_ANALYSIS_ENABLED = True
    FUNDAMENTAL_ANALYSIS_ENABLED = True

config = Config() 