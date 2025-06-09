# 🤖 AI Stock Trading Platform

A comprehensive, AI-powered stock trading platform that leverages multiple intelligent agents for automated trading decisions, risk management, and portfolio optimization.

## 🚀 Features

### 🧠 Multi-Agent AI System
- **Technical Analysis Agent**: Advanced technical indicator analysis using RSI, MACD, Bollinger Bands, and more
- **Sentiment Analysis Agent**: Market sentiment analysis from news and social signals
- **Risk Management Agent**: Portfolio risk assessment and position sizing optimization
- **Consensus Decision Making**: Intelligent combination of multiple agent signals

### 📊 Real-Time Market Analysis
- Live stock data integration via Yahoo Finance
- Technical indicator calculations and analysis
- Support and resistance level identification
- Volatility analysis and trend detection

### 💼 Portfolio Management
- Automated position sizing based on risk tolerance
- Real-time portfolio valuation and P&L tracking
- Trade execution and history logging
- Comprehensive performance analytics

### 🎯 Interactive Dashboard
- Modern Streamlit-based web interface
- Real-time portfolio monitoring
- AI signal visualization
- Manual trading capabilities
- Risk analysis tools

### ⚙️ Configurable & Extensible
- Flexible configuration system
- Multiple trading modes (paper/live)
- Customizable risk parameters
- Easy agent extension framework

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Streamlit     │    │   FastAPI       │    │   Trading       │
│   Frontend      │◄──►│   Backend       │◄──►│   Engine        │
│   (Port 8501)   │    │   (Port 8000)   │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │                        │
                                ▼                        ▼
                       ┌─────────────────┐    ┌─────────────────┐
                       │   Database      │    │   AI Agents     │
                       │   (SQLite)      │    │   - Technical   │
                       │                 │    │   - Sentiment   │
                       └─────────────────┘    │   - Risk Mgmt   │
                                              └─────────────────┘
```

## 📦 Installation

### Prerequisites
- Python 3.8 or higher
- pip package manager

### Quick Start

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd stock-trading-app
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Setup the application**
   ```bash
   python main.py --mode setup
   ```
   This will create a `.env` file and initialize the database.

4. **Configure API keys** (Optional but recommended)
   Edit the `.env` file and add your API keys:
   ```env
   OPENAI_API_KEY=your_openai_api_key_here
   ALPHA_VANTAGE_API_KEY=your_alpha_vantage_api_key_here
   ```

5. **Run the application**
   ```bash
   # Run everything (recommended for first-time users)
   python main.py --mode all
   
   # Or run components separately:
   python main.py --mode api       # API server only
   python main.py --mode frontend  # Web interface only
   python main.py --mode trading   # Trading engine only
   ```

6. **Access the web interface**
   Open your browser and go to `http://localhost:8501`

## 🎮 Usage

### Web Dashboard

1. **Dashboard**: Overview of portfolio performance, recent trades, and AI agent activity
2. **Portfolio**: Detailed portfolio management and position tracking
3. **Trading**: Manual trading interface with real-time market data
4. **AI Analysis**: Get AI-powered analysis for any stock symbol
5. **Risk Management**: Portfolio risk analysis and position sizing recommendations
6. **Settings**: Watchlist management and configuration

### API Endpoints

The FastAPI backend provides comprehensive REST endpoints:

- `GET /api/portfolio` - Portfolio summary
- `POST /api/trade` - Execute trades
- `POST /api/analyze` - AI stock analysis
- `GET /api/market/{symbol}` - Market data
- `POST /api/trading/start` - Start automated trading
- `GET /api/dashboard` - Dashboard data

API documentation is available at `http://localhost:8000/docs`

### Command Line Interface

```bash
# Setup and initialization
python main.py --mode setup

# Run individual components
python main.py --mode api          # FastAPI server
python main.py --mode frontend     # Streamlit UI
python main.py --mode trading      # AI trading engine

# Run everything together
python main.py --mode all
```

## ⚙️ Configuration

Edit `config.py` or `.env` file to customize:

```python
# Trading Configuration
RISK_TOLERANCE = "medium"      # low, medium, high
MAX_POSITION_SIZE = 0.1        # 10% of portfolio max
TRADING_MODE = "paper"         # paper or live trading
INITIAL_BALANCE = 100000.0     # Starting portfolio value

# Risk Management
STOP_LOSS_PERCENTAGE = 0.05    # 5% stop loss
TAKE_PROFIT_PERCENTAGE = 0.15  # 15% take profit

# AI Configuration
AI_UPDATE_INTERVAL = 300       # 5 minutes between analysis
```

## 🤖 AI Agents

### Technical Analysis Agent
- **Indicators**: RSI, MACD, Bollinger Bands, Moving Averages, Stochastic
- **Signals**: Trend identification, momentum analysis, support/resistance
- **Confidence**: Based on signal strength and volume confirmation

### Sentiment Analysis Agent
- **Sources**: Market sentiment indicators, volume analysis, momentum
- **Analysis**: News sentiment scoring, market behavior patterns
- **Integration**: Real-time sentiment tracking and analysis

### Risk Management Agent
- **Metrics**: Portfolio concentration, sector allocation, volatility
- **Assessment**: Position sizing, correlation analysis, drawdown limits
- **Optimization**: Dynamic risk adjustment based on market conditions

## 📈 Trading Strategy

The platform uses a consensus-based approach:

1. **Data Collection**: Real-time market data and historical analysis
2. **Agent Analysis**: Each AI agent analyzes the data independently
3. **Signal Generation**: Agents produce buy/sell/hold signals with confidence scores
4. **Consensus Building**: Weighted combination of agent signals
5. **Risk Assessment**: Risk management agent validates the decision
6. **Execution**: Trades executed only with high confidence and agreement
7. **Monitoring**: Continuous position monitoring and risk management

## 🔒 Safety Features

- **Paper Trading Mode**: Test strategies without real money
- **Risk Limits**: Automatic position sizing and risk controls
- **Stop Losses**: Configurable stop-loss and take-profit levels
- **Portfolio Limits**: Maximum position and sector concentration limits
- **Human Override**: Manual control and intervention capabilities

## 📊 Performance Monitoring

- Real-time portfolio valuation
- Trade history and performance analytics
- AI agent performance tracking
- Risk metrics and drawdown analysis
- Comparative benchmark analysis

## 🛠️ Development

### Project Structure
```
stock-trading-app/
├── agents/                 # AI trading agents
│   ├── base_agent.py      # Base agent class
│   ├── technical_agent.py # Technical analysis
│   ├── sentiment_agent.py # Sentiment analysis
│   └── risk_agent.py      # Risk management
├── api/                   # FastAPI backend
│   └── main.py           # API endpoints
├── frontend/              # Streamlit frontend
│   └── app.py            # Web interface
├── models/                # Database models
│   └── database.py       # SQLAlchemy models
├── services/              # Business logic
│   ├── data_service.py   # Market data service
│   └── portfolio_service.py # Portfolio management
├── trading_engine.py      # Main trading orchestrator
├── config.py             # Configuration
├── main.py               # Application entry point
└── requirements.txt      # Dependencies
```

### Adding New Agents

1. Create a new agent class inheriting from `BaseAgent`
2. Implement the `analyze()` method
3. Add the agent to the trading engine
4. Configure agent weights in the consensus calculation

### Extending Data Sources

1. Add new data provider in `services/data_service.py`
2. Implement data fetching and normalization
3. Update agents to use new data sources
4. Add API endpoints if needed

## 🚨 Disclaimer

**IMPORTANT**: This is a educational/demonstration trading platform. 

- **Not Financial Advice**: This software is for educational purposes only
- **Use at Your Own Risk**: Trading involves substantial risk of loss
- **Test First**: Always use paper trading mode before live trading
- **No Guarantees**: Past performance does not guarantee future results
- **Regulatory Compliance**: Ensure compliance with your local regulations

## 📄 License

This project is provided as-is for educational purposes. Please review and comply with all applicable financial regulations in your jurisdiction.

## 🤝 Contributing

Contributions are welcome! Please read the contributing guidelines and submit pull requests for any improvements.

## 📞 Support

For questions and support:
- Check the documentation in the code
- Review the API documentation at `/docs`
- Open an issue for bugs or feature requests

---

**Happy Trading!** 🚀📈🤖 