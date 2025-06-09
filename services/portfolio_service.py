from typing import Dict, List, Optional
from sqlalchemy.orm import Session
from models.database import Portfolio, Position, Trade, Stock, get_db
from services.data_service import data_service
from config import config
import asyncio
from datetime import datetime

class PortfolioService:
    def __init__(self):
        self.db = next(get_db())
    
    async def get_or_create_portfolio(self, portfolio_name: str = "Main Portfolio") -> Portfolio:
        """Get or create a portfolio"""
        portfolio = self.db.query(Portfolio).filter(Portfolio.name == portfolio_name).first()
        
        if not portfolio:
            portfolio = Portfolio(
                name=portfolio_name,
                cash_balance=config.INITIAL_BALANCE,
                total_value=config.INITIAL_BALANCE
            )
            self.db.add(portfolio)
            self.db.commit()
            self.db.refresh(portfolio)
        
        return portfolio
    
    async def execute_trade(self, symbol: str, action: str, quantity: int, 
                          strategy: str, confidence: float, portfolio_id: int = None) -> Dict:
        """Execute a trade (paper trading for now)"""
        try:
            # Get portfolio
            if portfolio_id is None:
                portfolio = await self.get_or_create_portfolio()
            else:
                portfolio = self.db.query(Portfolio).filter(Portfolio.id == portfolio_id).first()
            
            if not portfolio:
                return {"error": "Portfolio not found"}
            
            # Get current price
            price_data = await data_service.get_real_time_price(symbol)
            current_price = price_data.get('price', 0)
            
            if current_price <= 0:
                return {"error": f"Could not get price for {symbol}"}
            
            total_amount = quantity * current_price
            
            # Check if we have enough cash for buy orders
            if action == "buy" and portfolio.cash_balance < total_amount:
                return {"error": "Insufficient cash balance"}
            
            # Get or create stock record
            stock = self.db.query(Stock).filter(Stock.symbol == symbol).first()
            if not stock:
                stock_info = await data_service.get_stock_info(symbol)
                stock = Stock(
                    symbol=symbol,
                    name=stock_info.get('name', symbol),
                    sector=stock_info.get('sector', 'Unknown'),
                    market_cap=stock_info.get('market_cap', 0)
                )
                self.db.add(stock)
                self.db.commit()
                self.db.refresh(stock)
            
            # Create trade record
            trade = Trade(
                portfolio_id=portfolio.id,
                symbol=symbol,
                side=action,
                quantity=quantity,
                price=current_price,
                total_amount=total_amount,
                strategy=strategy,
                confidence_score=confidence
            )
            self.db.add(trade)
            
            # Update position
            await self._update_position(portfolio.id, stock.id, symbol, action, quantity, current_price)
            
            # Update portfolio cash balance
            if action == "buy":
                portfolio.cash_balance -= total_amount
            elif action == "sell":
                portfolio.cash_balance += total_amount
            
            # Update total portfolio value
            portfolio.total_value = await self._calculate_portfolio_value(portfolio.id)
            portfolio.updated_at = datetime.utcnow()
            
            self.db.commit()
            
            return {
                "success": True,
                "trade_id": trade.id,
                "symbol": symbol,
                "action": action,
                "quantity": quantity,
                "price": current_price,
                "total_amount": total_amount,
                "remaining_cash": portfolio.cash_balance
            }
            
        except Exception as e:
            self.db.rollback()
            return {"error": f"Trade execution failed: {str(e)}"}
    
    async def _update_position(self, portfolio_id: int, stock_id: int, symbol: str, 
                             action: str, quantity: int, price: float):
        """Update position based on trade"""
        position = self.db.query(Position).filter(
            Position.portfolio_id == portfolio_id,
            Position.symbol == symbol
        ).first()
        
        if not position:
            if action == "buy":
                position = Position(
                    portfolio_id=portfolio_id,
                    stock_id=stock_id,
                    symbol=symbol,
                    quantity=quantity,
                    average_price=price,
                    current_price=price
                )
                self.db.add(position)
        else:
            if action == "buy":
                # Update average price
                total_cost = (position.quantity * position.average_price) + (quantity * price)
                total_quantity = position.quantity + quantity
                position.average_price = total_cost / total_quantity
                position.quantity = total_quantity
                position.current_price = price
            elif action == "sell":
                position.quantity -= quantity
                position.current_price = price
                
                # Remove position if quantity becomes 0
                if position.quantity <= 0:
                    self.db.delete(position)
                    return
        
        # Calculate unrealized P&L
        if position and position.quantity > 0:
            position.unrealized_pnl = (position.current_price - position.average_price) * position.quantity
            position.updated_at = datetime.utcnow()
    
    async def _calculate_portfolio_value(self, portfolio_id: int) -> float:
        """Calculate total portfolio value"""
        portfolio = self.db.query(Portfolio).filter(Portfolio.id == portfolio_id).first()
        if not portfolio:
            return 0.0
        
        total_value = portfolio.cash_balance
        
        # Add value of all positions
        positions = self.db.query(Position).filter(Position.portfolio_id == portfolio_id).all()
        
        for position in positions:
            # Get current price
            price_data = await data_service.get_real_time_price(position.symbol)
            current_price = price_data.get('price', position.current_price)
            
            position.current_price = current_price
            position.unrealized_pnl = (current_price - position.average_price) * position.quantity
            
            total_value += current_price * position.quantity
        
        self.db.commit()
        return total_value
    
    async def get_portfolio_summary(self, portfolio_id: int = None) -> Dict:
        """Get portfolio summary with current positions"""
        if portfolio_id is None:
            portfolio = await self.get_or_create_portfolio()
        else:
            portfolio = self.db.query(Portfolio).filter(Portfolio.id == portfolio_id).first()
        
        if not portfolio:
            return {"error": "Portfolio not found"}
        
        # Update portfolio value
        current_value = await self._calculate_portfolio_value(portfolio.id)
        portfolio.total_value = current_value
        self.db.commit()
        
        # Get positions
        positions = self.db.query(Position).filter(Position.portfolio_id == portfolio.id).all()
        
        position_data = []
        total_unrealized_pnl = 0.0
        
        for position in positions:
            position_value = position.current_price * position.quantity
            pnl_percentage = ((position.current_price - position.average_price) / position.average_price) * 100
            
            position_data.append({
                "symbol": position.symbol,
                "quantity": position.quantity,
                "average_price": position.average_price,
                "current_price": position.current_price,
                "market_value": position_value,
                "unrealized_pnl": position.unrealized_pnl,
                "pnl_percentage": pnl_percentage
            })
            
            total_unrealized_pnl += position.unrealized_pnl
        
        # Calculate performance metrics
        initial_investment = config.INITIAL_BALANCE
        total_return = current_value - initial_investment
        total_return_percentage = (total_return / initial_investment) * 100
        
        return {
            "portfolio_id": portfolio.id,
            "name": portfolio.name,
            "cash_balance": portfolio.cash_balance,
            "total_value": current_value,
            "total_return": total_return,
            "total_return_percentage": total_return_percentage,
            "unrealized_pnl": total_unrealized_pnl,
            "positions": position_data,
            "positions_count": len(position_data)
        }
    
    async def get_trade_history(self, portfolio_id: int = None, limit: int = 50) -> List[Dict]:
        """Get trade history"""
        if portfolio_id is None:
            portfolio = await self.get_or_create_portfolio()
            portfolio_id = portfolio.id
        
        trades = self.db.query(Trade).filter(
            Trade.portfolio_id == portfolio_id
        ).order_by(Trade.executed_at.desc()).limit(limit).all()
        
        return [
            {
                "id": trade.id,
                "symbol": trade.symbol,
                "side": trade.side,
                "quantity": trade.quantity,
                "price": trade.price,
                "total_amount": trade.total_amount,
                "strategy": trade.strategy,
                "confidence_score": trade.confidence_score,
                "executed_at": trade.executed_at
            }
            for trade in trades
        ]
    
    async def get_position_by_symbol(self, symbol: str, portfolio_id: int = None) -> Optional[Dict]:
        """Get position for a specific symbol"""
        if portfolio_id is None:
            portfolio = await self.get_or_create_portfolio()
            portfolio_id = portfolio.id
        
        position = self.db.query(Position).filter(
            Position.portfolio_id == portfolio_id,
            Position.symbol == symbol
        ).first()
        
        if not position:
            return None
        
        # Update current price
        price_data = await data_service.get_real_time_price(symbol)
        current_price = price_data.get('price', position.current_price)
        
        position.current_price = current_price
        position.unrealized_pnl = (current_price - position.average_price) * position.quantity
        self.db.commit()
        
        return {
            "symbol": position.symbol,
            "quantity": position.quantity,
            "average_price": position.average_price,
            "current_price": position.current_price,
            "market_value": current_price * position.quantity,
            "unrealized_pnl": position.unrealized_pnl,
            "pnl_percentage": ((current_price - position.average_price) / position.average_price) * 100
        }

# Global instance
portfolio_service = PortfolioService() 