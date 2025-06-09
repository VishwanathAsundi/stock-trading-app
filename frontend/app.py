import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import asyncio
import json

# Configure Streamlit page
st.set_page_config(
    page_title="AI Stock Trading Platform",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# API base URL
API_BASE_URL = "http://localhost:8000"

# Custom CSS for better styling
st.markdown("""
<style>
.metric-card {
    background-color: #f0f2f6;
    padding: 1rem;
    border-radius: 0.5rem;
    border-left: 4px solid #ff6b6b;
}
.positive {
    color: #28a745;
}
.negative {
    color: #dc3545;
}
.neutral {
    color: #6c757d;
}
</style>
""", unsafe_allow_html=True)

def get_api_data(endpoint):
    """Fetch data from API"""
    try:
        response = requests.get(f"{API_BASE_URL}{endpoint}")
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"API Error: {e}")
        return None

def post_api_data(endpoint, data):
    """Post data to API"""
    try:
        response = requests.post(f"{API_BASE_URL}{endpoint}", json=data)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"API Error: {e}")
        return None

def delete_api_data(endpoint):
    """Delete data via API"""
    try:
        response = requests.delete(f"{API_BASE_URL}{endpoint}")
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"API Error: {e}")
        return None

def format_currency(value):
    """Format currency values"""
    return f"${value:,.2f}"

def format_percentage(value):
    """Format percentage values"""
    return f"{value:.2f}%"

def get_color_for_change(value):
    """Get color based on positive/negative change"""
    if value > 0:
        return "positive"
    elif value < 0:
        return "negative"
    else:
        return "neutral"

# Sidebar
st.sidebar.title("🤖 AI Trading Platform")

# Navigation
page = st.sidebar.selectbox(
    "Navigate",
    ["Dashboard", "Portfolio", "Trading", "AI Analysis", "Risk Management", "Settings"]
)

# Trading Engine Status
st.sidebar.markdown("---")
st.sidebar.markdown("### Trading Engine")

trading_status = get_api_data("/api/trading/status")
if trading_status:
    status_color = "🟢" if trading_status['is_running'] else "🔴"
    st.sidebar.markdown(f"{status_color} **Status:** {'Running' if trading_status['is_running'] else 'Stopped'}")
    
    col1, col2 = st.sidebar.columns(2)
    with col1:
        if st.button("Start", disabled=trading_status['is_running']):
            result = post_api_data("/api/trading/start", {})
            if result:
                st.rerun()
    
    with col2:
        if st.button("Stop", disabled=not trading_status['is_running']):
            result = post_api_data("/api/trading/stop", {})
            if result:
                st.rerun()

# Main content based on selected page
if page == "Dashboard":
    st.title("📊 Trading Dashboard")
    
    # Get dashboard data
    dashboard_data = get_api_data("/api/dashboard")
    
    if dashboard_data:
        portfolio = dashboard_data['portfolio']
        
        # Portfolio Overview Cards
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "Total Portfolio Value",
                format_currency(portfolio['total_value']),
                f"{format_percentage(portfolio['total_return_percentage'])}"
            )
        
        with col2:
            st.metric(
                "Cash Balance", 
                format_currency(portfolio['cash_balance'])
            )
        
        with col3:
            st.metric(
                "Unrealized P&L",
                format_currency(portfolio['unrealized_pnl']),
                f"{format_percentage(portfolio['unrealized_pnl']/portfolio['total_value']*100) if portfolio['total_value'] > 0 else '0.00%'}"
            )
        
        with col4:
            st.metric(
                "Active Positions",
                portfolio['positions_count']
            )
        
        # Charts Section
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("🎯 Watchlist")
            watchlist_data = dashboard_data.get('watchlist', [])
            
            if watchlist_data:
                watchlist_df = pd.DataFrame(watchlist_data)
                
                fig = px.bar(
                    watchlist_df, 
                    x='symbol', 
                    y='change_percent',
                    color='change_percent',
                    color_continuous_scale='RdYlGn',
                    title="Daily Change %"
                )
                fig.update_layout(height=400)
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No watchlist data available")
        
        with col2:
            st.subheader("🤖 Agent Performance")
            agent_perf = dashboard_data.get('agent_performance', {})
            
            if agent_perf:
                agent_df = pd.DataFrame([
                    {
                        'Agent': name,
                        'Total Signals': data['total_signals'],
                        'Avg Confidence': data['avg_confidence']
                    }
                    for name, data in agent_perf.items()
                ])
                
                fig = px.scatter(
                    agent_df,
                    x='Total Signals',
                    y='Avg Confidence',
                    size='Total Signals',
                    color='Agent',
                    title="Agent Activity vs Confidence"
                )
                fig.update_layout(height=400)
                st.plotly_chart(fig, use_container_width=True)
        
        # Recent Trades
        st.subheader("📈 Recent Trades")
        recent_trades = dashboard_data.get('recent_trades', [])
        
        if recent_trades:
            trades_df = pd.DataFrame(recent_trades)
            trades_df['executed_at'] = pd.to_datetime(trades_df['executed_at'])
            
            # Style the dataframe
            styled_df = trades_df.style.format({
                'price': lambda x: f"${x:.2f}",
                'total_amount': lambda x: f"${x:.2f}",
                'confidence_score': lambda x: f"{x:.2f}"
            })
            
            st.dataframe(styled_df, use_container_width=True)
        else:
            st.info("No recent trades")

elif page == "Portfolio":
    st.title("💼 Portfolio Management")
    
    # Get portfolio data
    portfolio_data = get_api_data("/api/portfolio")
    
    if portfolio_data:
        # Portfolio Summary
        st.subheader("Portfolio Summary")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Value", format_currency(portfolio_data['total_value']))
        with col2:
            st.metric("Total Return", format_currency(portfolio_data['total_return']))
        with col3:
            st.metric("Return %", format_percentage(portfolio_data['total_return_percentage']))
        
        # Positions
        st.subheader("Current Positions")
        
        if portfolio_data['positions']:
            positions_df = pd.DataFrame(portfolio_data['positions'])
            
            # Create allocation pie chart
            fig = px.pie(
                positions_df, 
                values='market_value', 
                names='symbol',
                title="Portfolio Allocation"
            )
            
            col1, col2 = st.columns([2, 1])
            with col1:
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                st.markdown("### Position Details")
                for _, position in positions_df.iterrows():
                    pnl_color = get_color_for_change(position['pnl_percentage'])
                    st.markdown(f"""
                    **{position['symbol']}**
                    - Quantity: {position['quantity']}
                    - Avg Price: {format_currency(position['average_price'])}
                    - Current: {format_currency(position['current_price'])}
                    - P&L: <span class="{pnl_color}">{format_currency(position['unrealized_pnl'])} ({format_percentage(position['pnl_percentage'])})</span>
                    """, unsafe_allow_html=True)
        else:
            st.info("No positions currently held")
        
        # Trade History
        st.subheader("Trade History")
        trades_data = get_api_data("/api/portfolio/trades?limit=20")
        
        if trades_data and trades_data['trades']:
            trades_df = pd.DataFrame(trades_data['trades'])
            trades_df['executed_at'] = pd.to_datetime(trades_df['executed_at'])
            
            st.dataframe(
                trades_df.style.format({
                    'price': lambda x: f"${x:.2f}",
                    'total_amount': lambda x: f"${x:.2f}",
                    'confidence_score': lambda x: f"{x:.2f}"
                }),
                use_container_width=True
            )

elif page == "Trading":
    st.title("💹 Manual Trading")
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader("Execute Trade")
        
        # Trade form
        with st.form("trade_form"):
            symbol = st.text_input("Symbol", placeholder="e.g., AAPL")
            action = st.selectbox("Action", ["buy", "sell"])
            quantity = st.number_input("Quantity", min_value=1, value=1)
            strategy = st.text_input("Strategy", value="Manual Trade")
            
            if st.form_submit_button("Execute Trade"):
                if symbol:
                    trade_data = {
                        "symbol": symbol.upper(),
                        "action": action,
                        "quantity": quantity,
                        "strategy": strategy
                    }
                    
                    result = post_api_data("/api/trade", trade_data)
                    
                    if result:
                        if result.get('success'):
                            st.success(f"Trade executed successfully! Trade ID: {result['trade_id']}")
                        else:
                            st.error(f"Trade failed: {result.get('error', 'Unknown error')}")
                else:
                    st.error("Please enter a symbol")
    
    with col2:
        st.subheader("Market Data")
        
        # Market data lookup
        lookup_symbol = st.text_input("Look up symbol", placeholder="e.g., TSLA")
        
        if lookup_symbol:
            market_data = get_api_data(f"/api/market/{lookup_symbol}")
            
            if market_data:
                current_price = market_data['current_price']
                
                # Price display
                if current_price:
                    change_color = get_color_for_change(current_price.get('change_percent', 0))
                    
                    st.markdown(f"""
                    ### {lookup_symbol.upper()}
                    **Price:** ${current_price.get('price', 0):.2f}
                    
                    **Change:** <span class="{change_color}">${current_price.get('change', 0):.2f} ({current_price.get('change_percent', 0):.2f}%)</span>
                    
                    **Volume:** {current_price.get('volume', 0):,}
                    """, unsafe_allow_html=True)
                
                # Historical chart
                historical = market_data.get('historical_data', {})
                if historical and historical.get('timestamps'):
                    chart_df = pd.DataFrame({
                        'timestamp': pd.to_datetime(historical['timestamps']),
                        'close': historical['close']
                    })
                    
                    fig = px.line(
                        chart_df, 
                        x='timestamp', 
                        y='close',
                        title=f"{lookup_symbol.upper()} Price Chart"
                    )
                    st.plotly_chart(fig, use_container_width=True)

elif page == "AI Analysis":
    st.title("🧠 AI Analysis")
    
    # Symbol input
    analysis_symbol = st.text_input("Enter symbol for AI analysis", placeholder="e.g., AAPL")
    
    if st.button("Analyze"):
        if analysis_symbol:
            # Get AI analysis
            analysis_data = post_api_data("/api/analyze", {"symbol": analysis_symbol})
            
            if analysis_data and 'error' not in analysis_data:
                st.subheader(f"AI Analysis for {analysis_symbol.upper()}")
                
                # Consensus
                consensus = analysis_data.get('consensus', {})
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    action_color = {
                        'buy': '🟢',
                        'sell': '🔴',
                        'hold': '🟡'
                    }.get(consensus.get('action', 'hold'), '🟡')
                    
                    st.metric("Consensus Action", f"{action_color} {consensus.get('action', 'N/A').upper()}")
                
                with col2:
                    st.metric("Confidence", f"{consensus.get('confidence', 0):.2f}")
                
                with col3:
                    st.metric("Agreement", f"{consensus.get('agreement', 0):.2f}")
                
                # Individual agent signals
                st.subheader("Agent Signals")
                
                signals = analysis_data.get('signals', {})
                
                for agent_name, signal_data in signals.items():
                    if 'error' not in signal_data:
                        with st.expander(f"{agent_name.title()} Agent"):
                            col1, col2 = st.columns(2)
                            
                            with col1:
                                st.write(f"**Action:** {signal_data['action'].upper()}")
                                st.write(f"**Confidence:** {signal_data['confidence']:.2f}")
                                
                                if signal_data.get('target_price'):
                                    st.write(f"**Target Price:** ${signal_data['target_price']:.2f}")
                                
                                if signal_data.get('stop_loss'):
                                    st.write(f"**Stop Loss:** ${signal_data['stop_loss']:.2f}")
                            
                            with col2:
                                st.write("**Reasoning:**")
                                st.write(signal_data.get('reasoning', 'No reasoning provided'))
                    else:
                        st.error(f"{agent_name} agent error: {signal_data['error']}")
            else:
                st.error("Failed to get AI analysis")

elif page == "Risk Management":
    st.title("⚠️ Risk Management")
    
    # Risk analysis for specific symbol
    st.subheader("Symbol Risk Analysis")
    
    risk_symbol = st.text_input("Enter symbol for risk analysis", placeholder="e.g., TSLA")
    
    if st.button("Analyze Risk"):
        if risk_symbol:
            risk_data = post_api_data("/api/risk/analyze", {"symbol": risk_symbol})
            
            if risk_data:
                risk_analysis = risk_data.get('risk_analysis', {})
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("Risk Action", risk_analysis.get('action', 'N/A').upper())
                
                with col2:
                    st.metric("Risk Confidence", f"{risk_analysis.get('confidence', 0):.2f}")
                
                with col3:
                    if risk_analysis.get('position_size'):
                        st.metric("Suggested Position Size", f"{risk_analysis['position_size']:.2%}")
                
                # Risk reasoning
                st.subheader("Risk Analysis")
                st.write(risk_analysis.get('reasoning', 'No risk analysis available'))
    
    # Portfolio risk overview
    st.subheader("Portfolio Risk Overview")
    portfolio_data = get_api_data("/api/portfolio")
    
    if portfolio_data and portfolio_data['positions']:
        positions_df = pd.DataFrame(portfolio_data['positions'])
        
        # Concentration risk
        total_value = portfolio_data['total_value']
        positions_df['allocation'] = positions_df['market_value'] / total_value * 100
        
        fig = px.bar(
            positions_df,
            x='symbol',
            y='allocation',
            title="Portfolio Concentration Risk",
            labels={'allocation': 'Allocation (%)'}
        )
        
        # Add risk threshold line
        fig.add_hline(y=20, line_dash="dash", line_color="red", 
                      annotation_text="High Risk Threshold (20%)")
        
        st.plotly_chart(fig, use_container_width=True)

elif page == "Settings":
    st.title("⚙️ Settings")
    
    # Watchlist management
    st.subheader("Watchlist Management")
    
    watchlist_data = get_api_data("/api/watchlist")
    
    if watchlist_data:
        current_watchlist = watchlist_data.get('watchlist', [])
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Current Watchlist:**")
            for symbol in current_watchlist:
                col_a, col_b = st.columns([3, 1])
                with col_a:
                    st.write(symbol)
                with col_b:
                    if st.button("Remove", key=f"remove_{symbol}"):
                        result = delete_api_data(f"/api/watchlist/remove/{symbol}")
                        if result:
                            st.rerun()
        
        with col2:
            st.write("**Add Symbol:**")
            new_symbol = st.text_input("Symbol", placeholder="e.g., AAPL")
            
            if st.button("Add to Watchlist"):
                if new_symbol:
                    result = post_api_data("/api/watchlist/add", {"symbol": new_symbol})
                    if result:
                        st.success(f"Added {new_symbol.upper()} to watchlist")
                        st.rerun()
    
    # Configuration settings
    st.subheader("Configuration")
    
    st.info("Configuration settings can be modified in the config.py file:")
    st.code("""
    # Trading Configuration
    RISK_TOLERANCE = "medium"  # low, medium, high
    MAX_POSITION_SIZE = 0.1    # 10% of portfolio
    TRADING_MODE = "paper"     # paper, live
    
    # Portfolio Settings
    INITIAL_BALANCE = 100000.0
    STOP_LOSS_PERCENTAGE = 0.05
    TAKE_PROFIT_PERCENTAGE = 0.15
    """)

# Auto-refresh for dashboard
if page == "Dashboard":
    st.sidebar.markdown("---")
    if st.sidebar.button("🔄 Refresh Dashboard"):
        st.rerun()
    
    # Auto-refresh every 30 seconds if enabled
    auto_refresh = st.sidebar.checkbox("Auto-refresh (30s)")
    if auto_refresh:
        st.rerun() 