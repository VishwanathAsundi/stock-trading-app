from .base_agent import BaseAgent, TradingSignal
import pandas as pd
from typing import Dict, List, Tuple
import numpy as np
# from services.portfolio_service import portfolio_service  # TODO: Implement or provide portfolio_service

class RiskManagementAgent(BaseAgent):
    def __init__(self):
        super().__init__("Risk Management Agent")
        self.max_portfolio_risk = 0.02  # 2% max portfolio risk per trade
        self.max_sector_allocation = 0.3  # 30% max allocation per sector
        self.max_correlation_exposure = 0.5  # 50% max exposure to highly correlated assets

    async def analyze(self, symbol: str, data: pd.DataFrame, market_data: Dict) -> TradingSignal:
        """Analyze risk factors and generate risk-adjusted trading signal"""
        current_price = data['Close'].iloc[-1] if not data.empty else market_data.get('price', 0.0)

        # Get current portfolio state
        # portfolio_summary = await portfolio_service.get_portfolio_summary() # TODO: Implement or provide portfolio_service
        portfolio_summary = {
            "total_value": 100000.0,
            "cash_balance": 50000.0,
            "positions": [
                {"symbol": "AAPL", "market_value": 20000.0},
                {"symbol": "GOOGL", "market_value": 15000.0}
            ]
        }

        # Calculate various risk metrics
        risk_metrics = await self._calculate_risk_metrics(symbol, data, portfolio_summary)

        # Determine risk-adjusted action
        action, confidence = self._determine_risk_adjusted_action(risk_metrics, symbol, current_price)

        # Generate risk-based reasoning
        reasoning = self._generate_risk_reasoning(risk_metrics, symbol)

        # Get AI-enhanced risk analysis
        ai_prompt = (
            f"Risk analysis for {symbol}:\n"
            f"Current Price: ${current_price:.2f}\n"
            f"Portfolio Risk Score: {risk_metrics['portfolio_risk']:.2f}\n"
            f"Position Risk: {risk_metrics['position_risk']:.2f}\n"
            f"Volatility: {risk_metrics['volatility']:.2f}\n"
            f"Sector Concentration: {risk_metrics['sector_risk']:.2f}\n"
            f"Cash Ratio: {risk_metrics['cash_ratio']:.2f}\n\n"
            f"Recommended Action: {action}\n"
            f"Risk Level: {risk_metrics['overall_risk_level']}\n\n"
            f"Provide risk management recommendations and position sizing guidance."
        )

        ai_analysis = await self._get_ai_analysis(ai_prompt)

        signal = TradingSignal(
            symbol=symbol,
            action=action,
            confidence=confidence,
            reasoning=f"{reasoning}\n\nAI Risk Analysis: {ai_analysis}",
            target_price=self._calculate_take_profit(current_price, action),
            stop_loss=self._calculate_stop_loss(current_price, action),
            position_size=self._calculate_risk_adjusted_position_size(risk_metrics, portfolio_summary['total_value'])
        )

        self.record_signal(signal)
        return signal

    async def _calculate_risk_metrics(self, symbol: str, data: pd.DataFrame, portfolio_summary: Dict) -> Dict:
        """Calculate comprehensive risk metrics"""
        metrics = {}

        # Portfolio-level metrics
        total_value = portfolio_summary.get('total_value', 0.0)
        cash_balance = portfolio_summary.get('cash_balance', 0.0)
        positions = portfolio_summary.get('positions', [])

        # Cash ratio
        metrics['cash_ratio'] = cash_balance / total_value if total_value > 0 else 1.0

        # Portfolio concentration risk
        metrics['concentration_risk'] = self._calculate_concentration_risk(positions, total_value)

        # Sector risk
        metrics['sector_risk'] = await self._calculate_sector_risk(positions, symbol)

        # Individual position risk
        metrics['position_risk'] = self._calculate_position_risk(symbol, data, total_value)

        # Volatility risk
        metrics['volatility'] = self._calculate_volatility_risk(data)

        # Correlation risk (simplified)
        metrics['correlation_risk'] = await self._calculate_correlation_risk(symbol, positions)

        # Overall portfolio risk
        metrics['portfolio_risk'] = self._calculate_overall_portfolio_risk(metrics)

        # Risk level classification
        metrics['overall_risk_level'] = self._classify_risk_level(metrics['portfolio_risk'])

        return metrics

    def _calculate_concentration_risk(self, positions: List[Dict], total_value: float) -> float:
        """Calculate portfolio concentration risk"""
        if not positions or total_value <= 0:
            return 0.0

        # Calculate Herfindahl-Hirschman Index for concentration
        concentration_sum = 0.0
        for position in positions:
            weight = position['market_value'] / total_value
            concentration_sum += weight ** 2

        # Normalize to 0-1 scale (1 = fully concentrated, 0 = fully diversified)
        max_concentration = 1.0  # Single position
        min_concentration = 1.0 / len(positions) if positions else 1.0

        if max_concentration == min_concentration:
            normalized_concentration = 1.0
        else:
            normalized_concentration = (concentration_sum - min_concentration) / (max_concentration - min_concentration)
        return max(0.0, min(1.0, normalized_concentration))

    async def _calculate_sector_risk(self, positions: List[Dict], new_symbol: str) -> float:
        """Calculate sector concentration risk"""
        # This is simplified - in reality, you'd fetch sector data for all positions
        # For now, we'll assume a mock sector distribution

        sector_allocation = {}
        total_value = sum(pos['market_value'] for pos in positions)

        # Mock sector assignments (in real implementation, fetch from data service)
        mock_sectors = {
            'AAPL': 'Technology', 'GOOGL': 'Technology', 'MSFT': 'Technology',
            'TSLA': 'Automotive', 'AMZN': 'E-commerce', 'NVDA': 'Technology',
            'META': 'Technology', 'NFLX': 'Entertainment'
        }

        for position in positions:
            sector = mock_sectors.get(position['symbol'], 'Other')
            if sector not in sector_allocation:
                sector_allocation[sector] = 0.0
            sector_allocation[sector] += position['market_value']

        if total_value > 0:
            # Convert to percentages
            for sector in sector_allocation:
                sector_allocation[sector] /= total_value

        # Find maximum sector allocation
        max_sector_allocation = max(sector_allocation.values()) if sector_allocation else 0.0

        # Risk increases with sector concentration
        return min(1.0, max_sector_allocation / self.max_sector_allocation)

    def _calculate_position_risk(self, symbol: str, data: pd.DataFrame, portfolio_value: float) -> float:
        """Calculate individual position risk"""
        if data.empty or 'Close' not in data.columns:
            return 1.0  # High risk if no data

        # Price volatility
        returns = data['Close'].pct_change().dropna()
        if len(returns) < 2:
            return 1.0

        volatility = returns.std() * np.sqrt(252)  # Annualized volatility

        # Risk based on volatility (normalize to 0-1)
        volatility_risk = min(1.0, volatility / 0.5)  # 50% volatility = max risk

        return volatility_risk

    def _calculate_volatility_risk(self, data: pd.DataFrame) -> float:
        """Calculate volatility-based risk"""
        if data.empty or len(data) < 20 or 'Close' not in data.columns:
            return 0.5  # Medium risk if insufficient data

        # Calculate multiple volatility measures
        returns = data['Close'].pct_change().dropna()

        # Standard deviation
        std_vol = returns.std() * np.sqrt(252)

        # Average True Range (ATR) based volatility
        if all(col in data.columns for col in ['High', 'Low', 'Close']):
            high_low = data['High'] - data['Low']
            high_close = np.abs(data['High'] - data['Close'].shift())
            low_close = np.abs(data['Low'] - data['Close'].shift())

            true_range = pd.DataFrame({'hl': high_low, 'hc': high_close, 'lc': low_close}).max(axis=1)
            atr_vol = true_range.rolling(14).mean().iloc[-1] / data['Close'].iloc[-1]
        else:
            atr_vol = std_vol

        # Combine volatility measures
        combined_vol = (std_vol + atr_vol) / 2

        # Normalize to 0-1 scale
        return min(1.0, combined_vol / 0.6)  # 60% annualized vol = max risk

    async def _calculate_correlation_risk(self, symbol: str, positions: List[Dict]) -> float:
        """Calculate correlation risk (simplified)"""
        # This is a simplified correlation risk calculation
        # In reality, you'd calculate actual correlations between assets

        if not positions:
            return 0.0

        # Mock correlation matrix (simplified)
        high_correlation_pairs = [
            ['AAPL', 'MSFT'], ['GOOGL', 'META'], ['NVDA', 'AAPL'],
            ['TSLA', 'AAPL'], ['AMZN', 'GOOGL']
        ]

        correlation_risk = 0.0
        position_symbols = [pos['symbol'] for pos in positions]

        for pair in high_correlation_pairs:
            if symbol in pair and any(p_symbol in pair for p_symbol in position_symbols):
                correlation_risk += 0.2

        return min(1.0, correlation_risk)

    def _calculate_overall_portfolio_risk(self, metrics: Dict) -> float:
        """Calculate overall portfolio risk score"""
        weights = {
            'concentration_risk': 0.25,
            'sector_risk': 0.20,
            'position_risk': 0.20,
            'volatility': 0.20,
            'correlation_risk': 0.15
        }

        risk_score = 0.0
        for metric, weight in weights.items():
            risk_score += metrics.get(metric, 0.0) * weight

        # Adjust for cash ratio (more cash = lower risk)
        cash_adjustment = 1.0 - (metrics.get('cash_ratio', 0.0) * 0.3)

        return min(1.0, risk_score * cash_adjustment)

    def _classify_risk_level(self, risk_score: float) -> str:
        """Classify overall risk level"""
        if risk_score < 0.3:
            return "Low"
        elif risk_score < 0.6:
            return "Medium"
        elif risk_score < 0.8:
            return "High"
        else:
            return "Very High"

    def _determine_risk_adjusted_action(self, risk_metrics: Dict, symbol: str, current_price: float) -> Tuple[str, float]:
        """Determine action based on risk analysis"""
        portfolio_risk = risk_metrics['portfolio_risk']
        position_risk = risk_metrics['position_risk']
        cash_ratio = risk_metrics['cash_ratio']

        # Risk-based decision logic
        if portfolio_risk > 0.8:
            # Very high risk - only allow sells or holds
            return "sell", 0.8  # High confidence to reduce risk
        elif portfolio_risk > 0.6:
            # High risk - conservative approach
            if cash_ratio < 0.2:  # Low cash
                return "sell", 0.6
            else:
                return "hold", 0.4
        elif portfolio_risk < 0.3 and position_risk < 0.4:
            # Low risk - can consider buying
            return "buy", 0.5
        else:
            # Medium risk - hold or small positions only
            return "hold", 0.3

    def _calculate_risk_adjusted_position_size(self, risk_metrics: Dict, portfolio_value: float) -> float:
        """Calculate position size based on risk metrics"""
        base_size = self._calculate_position_size(0.05, portfolio_value)  # Base 5% position

        # Adjust based on various risk factors
        risk_adjustment = 1.0

        # Portfolio risk adjustment
        portfolio_risk = risk_metrics['portfolio_risk']
        if portfolio_risk > 0.6:
            risk_adjustment *= 0.5  # Reduce size by 50%
        elif portfolio_risk < 0.3:
            risk_adjustment *= 1.2  # Increase size by 20%

        # Position-specific risk adjustment
        position_risk = risk_metrics['position_risk']
        if position_risk > 0.6:
            risk_adjustment *= 0.7  # Reduce for high volatility

        # Cash ratio adjustment
        cash_ratio = risk_metrics['cash_ratio']
        if cash_ratio < 0.1:  # Very low cash
            risk_adjustment *= 0.3
        elif cash_ratio > 0.5:  # High cash
            risk_adjustment *= 1.1

        return base_size * risk_adjustment

    def _generate_risk_reasoning(self, risk_metrics: Dict, symbol: str) -> str:
        """Generate human-readable risk reasoning"""
        reasoning_parts = []

        # Portfolio risk
        portfolio_risk = risk_metrics['portfolio_risk']
        risk_level = risk_metrics['overall_risk_level']
        reasoning_parts.append(f"Overall portfolio risk: {risk_level} ({portfolio_risk:.2f})")

        # Concentration risk
        concentration = risk_metrics['concentration_risk']
        if concentration > 0.7:
            reasoning_parts.append("High portfolio concentration detected")
        elif concentration < 0.3:
            reasoning_parts.append("Portfolio well diversified")

        # Sector risk
        sector_risk = risk_metrics['sector_risk']
        if sector_risk > 0.7:
            reasoning_parts.append("High sector concentration risk")

        # Volatility
        volatility = risk_metrics['volatility']
        if volatility > 0.7:
            reasoning_parts.append(f"High volatility asset ({volatility:.2f})")
        elif volatility < 0.3:
            reasoning_parts.append("Low volatility asset")

        # Cash position
        cash_ratio = risk_metrics['cash_ratio']
        if cash_ratio < 0.1:
            reasoning_parts.append("Low cash reserves - consider reducing exposure")
        elif cash_ratio > 0.5:
            reasoning_parts.append("High cash reserves - opportunity for deployment")

        return ". ".join(reasoning_parts)