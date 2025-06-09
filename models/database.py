from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Boolean, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session, relationship
from datetime import datetime
from config import config

Base = declarative_base()

class Stock(Base):
    __tablename__ = "stocks"
    
    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String, unique=True, index=True)
    name = Column(String)
    sector = Column(String)
    market_cap = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    positions = relationship("Position", back_populates="stock")
    price_data = relationship("PriceData", back_populates="stock")

class Portfolio(Base):
    __tablename__ = "portfolios"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, default="Main Portfolio")
    cash_balance = Column(Float, default=config.INITIAL_BALANCE)
    total_value = Column(Float, default=config.INITIAL_BALANCE)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    positions = relationship("Position", back_populates="portfolio")
    trades = relationship("Trade", back_populates="portfolio")

class Position(Base):
    __tablename__ = "positions"
    
    id = Column(Integer, primary_key=True, index=True)
    portfolio_id = Column(Integer, ForeignKey("portfolios.id"))
    stock_id = Column(Integer, ForeignKey("stocks.id"))
    symbol = Column(String, index=True)
    quantity = Column(Integer)
    average_price = Column(Float)
    current_price = Column(Float)
    unrealized_pnl = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    portfolio = relationship("Portfolio", back_populates="positions")
    stock = relationship("Stock", back_populates="positions")

class Trade(Base):
    __tablename__ = "trades"
    
    id = Column(Integer, primary_key=True, index=True)
    portfolio_id = Column(Integer, ForeignKey("portfolios.id"))
    symbol = Column(String, index=True)
    side = Column(String)  # 'buy' or 'sell'
    quantity = Column(Integer)
    price = Column(Float)
    total_amount = Column(Float)
    strategy = Column(String)  # Which AI agent made this trade
    confidence_score = Column(Float)
    executed_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    portfolio = relationship("Portfolio", back_populates="trades")

class PriceData(Base):
    __tablename__ = "price_data"
    
    id = Column(Integer, primary_key=True, index=True)
    stock_id = Column(Integer, ForeignKey("stocks.id"))
    symbol = Column(String, index=True)
    timestamp = Column(DateTime)
    open_price = Column(Float)
    high_price = Column(Float)
    low_price = Column(Float)
    close_price = Column(Float)
    volume = Column(Integer)
    
    # Relationships
    stock = relationship("Stock", back_populates="price_data")

class AISignal(Base):
    __tablename__ = "ai_signals"
    
    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String, index=True)
    agent_name = Column(String)
    signal_type = Column(String)  # 'buy', 'sell', 'hold'
    confidence_score = Column(Float)
    reasoning = Column(Text)
    technical_indicators = Column(Text)  # JSON string
    sentiment_score = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)

# Database setup
engine = create_engine(config.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def create_tables():
    Base.metadata.create_all(bind=engine)

def get_db() -> Session:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close() 