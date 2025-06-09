import streamlit as st
import requests
import pandas as pd
import plotly.express as px

# Configure Streamlit page
st.set_page_config(
    page_title="AI Stock Analyzer",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

API_BASE_URL = "http://localhost:8000"

# Sidebar
with st.sidebar:
    st.title("📈 AI Stock Analyzer")
    st.markdown("""
    **Analyze any US stock with AI-powered technical and sentiment analysis.**
    
    - Type a company name or symbol (e.g., Apple, AAPL, Tesla, TSLA)
    - Click **Analyze**
    - View consensus, agent signals, and charts
    """)
    st.markdown("---")
    st.info("Made with ❤️ using Streamlit and Gemini AI")

st.markdown("""
<style>
.big-metric {
    font-size: 2.5rem !important;
    font-weight: bold;
    color: #2E8B57;
}
.consensus-action {
    font-size: 1.5rem !important;
    font-weight: bold;
    color: #0072C6;
}
</style>
""", unsafe_allow_html=True)

st.header("🔍 Stock Analysis Dashboard")
company_input = st.text_input(
    "Company Name or Symbol",
    value="",
    max_chars=40,
    help="Type a US company name or symbol (e.g., Apple, AAPL, Tesla, TSLA)"
)

analyze_btn = st.button("🚀 Analyze", use_container_width=True)

symbol = None

if analyze_btn:
    # Search for the company name or symbol using the backend
    try:
        print("company_input", company_input)
        resp = requests.get(f"{API_BASE_URL}/search", params={"q": company_input})
        print("resp", resp.json())
        if resp.status_code == 200:
            results = resp.json()
            print("results", results)
            # Use the first result if available
            if results:
                symbol = results[0]["symbol"]
            else:
                symbol = company_input
                st.warning("No US stock found for your input. Please try a different company or symbol.")
        else:
            st.error(f"Search API error: {resp.status_code} - {resp.text}")
    except Exception as e:
        st.error(f"Search error: {e}")
    
    print("symbol", symbol)

    if symbol:
        with st.spinner(f"Analyzing {symbol.upper()}..."):
            response = requests.post(f"{API_BASE_URL}/analyze", json={"symbol": symbol})
            if response.status_code == 200:
                data = response.json()
                if "error" in data:
                    st.error(data["error"])
                else:
                    st.success(f"Analysis complete for {symbol.upper()}! ✅")
                    # Layout: Metrics and Consensus
                    col1, col2, col3 = st.columns([2,2,3])
                    with col1:
                        st.metric("Current Price", f"${data['current_price']:.2f}")
                    with col2:
                        consensus = data.get("consensus", {})
                        action = consensus.get('action', 'N/A').upper()
                        st.markdown(f"<div class='consensus-action'>Consensus: {action}</div>", unsafe_allow_html=True)
                        st.markdown(f"**Confidence:** `{consensus.get('confidence', 0):.2f}`")
                        st.markdown(f"**Agent Agreement:** `{consensus.get('agreement', 0):.2f}`")
                    with col3:
                        st.info("""
                        **How to interpret:**
                        - **Buy**: Strong positive signals
                        - **Sell**: Strong negative signals
                        - **Hold**: Uncertain or mixed signals
                        """)
                    st.divider()
                    # Price Chart (if available)
                    if 'signals' in data and 'technical' in data['signals']:
                        tech = data['signals']['technical']
                        if 'reasoning' in tech and 'price history' in tech['reasoning'].lower():
                            pass  # Placeholder for future chart extraction
                    # Try to fetch price history for chart
                    try:
                        import yfinance as yf
                        hist = yf.Ticker(symbol).history(period="1mo", interval="1d")
                        if not hist.empty:
                            fig = px.line(hist, x=hist.index, y='Close', title=f"{symbol.upper()} Price (1 Month)")
                            st.plotly_chart(fig, use_container_width=True)
                    except Exception:
                        pass
                    st.subheader("🧠 Agent Signals")
                    signals = data.get("signals", {})
                    for agent, sig in signals.items():
                        with st.expander(f"{agent.title()} Agent", expanded=True):
                            if 'error' in sig:
                                st.error(sig['error'])
                            else:
                                st.write(f"**Action:** :dart: `{sig['action'].upper()}`")
                                st.write(f"**Confidence:** `{sig['confidence']:.2f}`")
                                if sig.get('target_price'):
                                    st.write(f"**Target Price:** :moneybag: `${sig['target_price']:.2f}`")
                                if sig.get('stop_loss'):
                                    st.write(f"**Stop Loss:** :no_entry: `${sig['stop_loss']:.2f}`")
                                st.write("**Reasoning:**")
                                st.write(sig.get('reasoning', 'No reasoning provided'))
            else:
                st.error(f"API Error: {response.status_code}") 