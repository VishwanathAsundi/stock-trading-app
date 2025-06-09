import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # API Keys
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
    TWELVE_DATA_API_KEY = os.getenv("TWELVE_DATA_API_KEY", "")
    
    # AI Agent Settings
    AI_UPDATE_INTERVAL = 300  # 5 minutes
    SENTIMENT_ANALYSIS_ENABLED = True
    TECHNICAL_ANALYSIS_ENABLED = True
    FUNDAMENTAL_ANALYSIS_ENABLED = True
    
    # Trading Parameters
    STOP_LOSS_PERCENTAGE = float(os.getenv("STOP_LOSS_PERCENTAGE", 0.05))  # 5%
    TAKE_PROFIT_PERCENTAGE = float(os.getenv("TAKE_PROFIT_PERCENTAGE", 0.15))  # 15%
    MAX_POSITION_SIZE = float(os.getenv("MAX_POSITION_SIZE", 0.1))  # 10%

config = Config() 