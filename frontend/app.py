import streamlit as st
import requests
import pandas as pd
import plotly.express as px

st.set_page_config(
    page_title="AI Stock Analyzer",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Custom CSS for a more interesting UI, especially agent signals ---
st.markdown("""
<style>
body {
    background: linear-gradient(120deg, #f0f4f8 0%, #e0eafc 100%);
    font-family: 'Segoe UI', 'Roboto', 'Helvetica Neue', Arial, 'Liberation Sans', sans-serif;
}
[data-testid="stSidebar"] {
    background: linear-gradient(135deg, #232526 0%, #414345 100%);
    color: #fff;
    font-family: 'Segoe UI', 'Roboto', 'Helvetica Neue', Arial, 'Liberation Sans', sans-serif;
}
.big-metric {
    font-size: 2.7rem !important;
    font-weight: bold;
    color: #2E8B57;
    text-shadow: 1px 1px 2px #b2f7ef;
    font-family: 'Montserrat', 'Segoe UI', 'Roboto', sans-serif;
}
.consensus-action {
    font-size: 1.7rem !important;
    font-weight: bold;
    color: #0072C6;
    text-shadow: 1px 1px 2px #b2d7ff;
    font-family: 'Montserrat', 'Segoe UI', 'Roboto', sans-serif;
}
.metric-label {
    font-size: 1.1rem !important;
    color: #555;
    font-family: 'Segoe UI', 'Roboto', 'Helvetica Neue', Arial, 'Liberation Sans', sans-serif;
}
.agent-expander {
    background: linear-gradient(120deg, #f7fafc 60%, #e0eafc 100%);
    border-radius: 14px;
    border: 1.5px solid #b2d7ff;
    margin-bottom: 14px;
    padding: 18px 18px 12px 18px;
    box-shadow: 0 2px 12px #b2d7ff22;
    font-family: 'Segoe UI', 'Roboto', 'Helvetica Neue', Arial, 'Liberation Sans', sans-serif;
}
.agent-action {
    font-size: 1.25rem;
    font-weight: 600;
    color: #2E8B57;
    letter-spacing: 0.5px;
    font-family: 'Montserrat', 'Segoe UI', 'Roboto', sans-serif;
    margin-bottom: 6px;
}
.agent-action.sell {
    color: #d32f2f;
}
.agent-action.hold {
    color: #ff9800;
}
.agent-confidence-bar {
    height: 18px;
    background: #e0eafc;
    border-radius: 9px;
    margin: 8px 0 12px 0;
    position: relative;
    width: 100%;
    overflow: hidden;
}
.agent-confidence-fill {
    height: 100%;
    border-radius: 9px;
    background: linear-gradient(90deg, #0072C6 0%, #2E8B57 100%);
    transition: width 0.5s;
}
.agent-confidence-label {
    position: absolute;
    left: 50%;
    top: 0;
    transform: translateX(-50%);
    font-size: 1.05rem;
    font-weight: 600;
    color: #0072C6;
    line-height: 18px;
    font-family: 'Montserrat', 'Segoe UI', 'Roboto', sans-serif;
}
.agent-target-stop {
    font-size: 1.08rem;
    margin-bottom: 4px;
    margin-top: 2px;
    color: #0072C6;
    font-family: 'Montserrat', 'Segoe UI', 'Roboto', sans-serif;
}
.agent-reasoning-title {
    font-size: 1.13rem;
    font-weight: 600;
    color: #2E8B57;
    margin-top: 10px;
    margin-bottom: 2px;
    font-family: 'Montserrat', 'Segoe UI', 'Roboto', sans-serif;
}
.agent-reasoning-body {
    font-size: 1.05rem;
    color: #333;
    font-family: 'Segoe UI', 'Roboto', 'Helvetica Neue', Arial, 'Liberation Sans', sans-serif;
    background: #f0f4f8;
    border-radius: 7px;
    padding: 8px 12px;
    margin-bottom: 0;
}
.stAlert {
    border-radius: 10px;
}
.stButton>button {
    background: linear-gradient(90deg, #0072C6 0%, #2E8B57 100%);
    color: white;
    font-weight: bold;
    border-radius: 8px;
    border: none;
    box-shadow: 0 2px 8px #b2f7ef44;
    font-family: 'Montserrat', 'Segoe UI', 'Roboto', sans-serif;
}
.stButton>button:hover {
    background: linear-gradient(90deg, #2E8B57 0%, #0072C6 100%);
    color: #fff;
}
</style>
""", unsafe_allow_html=True)

API_BASE_URL = "http://localhost:8000"

# Sidebar
with st.sidebar:
    st.image("https://img.icons8.com/color/96/000000/line-chart.png", width=80)
    st.title("📈 AI Stock Analyzer")
    st.markdown("""
    <div style="font-size:1.1rem;line-height:1.5;font-family:'Segoe UI','Roboto','Helvetica Neue',Arial,'Liberation Sans',sans-serif;">
    <b>Analyze any US or Indian stock with AI-powered technical and sentiment analysis.</b>
    <ul style="margin-top:0.5em;">
      <li>Type a company name or symbol (e.g., <b>Apple, AAPL, Reliance, RELIANCE.NSE, Tata, TCS.NSE</b>)</li>
      <li>Click <b>Analyze</b></li>
      <li>View <span style="color:#2E8B57;font-weight:bold;">consensus</span>, <span style="color:#0072C6;font-weight:bold;">agent signals</span>, and <span style="color:#ff9800;font-weight:bold;">charts</span></li>
    </ul>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("---")
    st.info("Made with ❤️ using Streamlit and Gemini AI")

st.markdown("<h1 style='text-align:center; color:#0072C6; font-size:2.3rem; font-family:Montserrat,Segoe UI,Roboto,sans-serif;'>🔍 Stock Analysis Dashboard</h1>", unsafe_allow_html=True)
company_input = st.text_input(
    "Company Name or Symbol",
    value="",
    max_chars=40,
    help="Type a US or Indian company name or symbol (e.g., Apple, AAPL, Reliance, RELIANCE.NSE, Tata, TCS.NSE)"
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
        print("symbol inside if", symbol)
        with st.spinner(f"Analyzing {symbol.upper()}..."):
            print("symbol inside if-2", symbol)
            response = requests.post(f"{API_BASE_URL}/analyze", json={"symbol": symbol})
            if response.status_code == 200:
                data = response.json()
                if "error" in data:
                    st.error(data["error"])
                else:
                    st.balloons()
                    st.success(f"Analysis complete for {symbol.upper()}! ✅")
                    currency = data.get('currency', '$')
                    # Layout: Metrics and Consensus
                    col1, col2, col3 = st.columns([2,2,3])
                    with col1:
                        st.markdown(f"<div class='metric-label'>Current Price</div>", unsafe_allow_html=True)
                        st.markdown(
                            f"<div class='big-metric'>{currency}{data['current_price']:.2f}</div>",
                            unsafe_allow_html=True
                        )
                    with col2:
                        consensus = data.get("consensus", {})
                        action = consensus.get('action', 'N/A').upper()
                        action_emoji = "🟢" if action == "BUY" else ("🔴" if action == "SELL" else "🟡")
                        st.markdown(
                            f"<div class='consensus-action'>{action_emoji} Consensus: {action}</div>",
                            unsafe_allow_html=True
                        )
                        st.progress(min(consensus.get('confidence', 0), 1.0), text="Confidence")
                        st.markdown(f"**Agent Agreement:** `{consensus.get('agreement', 0):.2f}`")
                    with col3:
                        st.info("💡 How to interpret:")
                        st.markdown("""
                        <ul>
                        <li><span style="color:#2E8B57;font-weight:bold;">Buy</span>: Strong positive signals</li>
                        <li><span style="color:#d32f2f;font-weight:bold;">Sell</span>: Strong negative signals</li>
                        <li><span style="color:#ff9800;font-weight:bold;">Hold</span>: Uncertain or mixed signals</li>
                        </ul>
                        """, unsafe_allow_html=True)
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
                            fig = px.line(
                                hist, x=hist.index, y='Close',
                                title=f"{symbol.upper()} Price (1 Month)",
                                template="plotly_white",
                                markers=True
                            )
                            fig.update_traces(line=dict(color="#0072C6", width=3))
                            fig.update_layout(
                                title_font=dict(size=20, color="#0072C6"),
                                xaxis_title="Date",
                                yaxis_title="Price",
                                plot_bgcolor="#f7fafc",
                                margin=dict(l=10, r=10, t=40, b=10)
                            )
                            st.plotly_chart(fig, use_container_width=True)
                    except Exception:
                        pass
                    st.subheader("🧠 Agent Signals")
                    signals = data.get("signals", {})
                    agent_icons = {
                        "technical": "📊",
                        "sentiment": "📰",
                        "risk": "⚠️",
                        "fundamental": "💼"
                    }
                    for agent, sig in signals.items():
                        icon = agent_icons.get(agent.lower(), "🤖")
                        with st.expander(f"{icon} {agent.title()} Agent", expanded=True):
                            st.markdown("<div class='agent-expander'>", unsafe_allow_html=True)
                            if 'error' in sig:
                                st.error(sig['error'])
                            else:
                                action = sig['action'].upper()
                                if action == "BUY":
                                    action_class = "buy"
                                    action_color = "#2E8B57"
                                elif action == "SELL":
                                    action_class = "sell"
                                    action_color = "#d32f2f"
                                else:
                                    action_class = "hold"
                                    action_color = "#ff9800"
                                action_emoji = "🟢" if action == "BUY" else ("🔴" if action == "SELL" else "🟡")
                                st.markdown(
                                    f"<div class='agent-action {action_class}' style='color:{action_color};font-family:Montserrat,Segoe UI,Roboto,sans-serif;'>"
                                    f"{action_emoji} <b>{action}</b>"
                                    "</div>",
                                    unsafe_allow_html=True
                                )
                                # Custom confidence bar
                                conf = min(sig['confidence'], 1.0)
                                st.markdown(
                                    f'''
                                    <div class="agent-confidence-bar">
                                        <div class="agent-confidence-fill" style="width:{conf*100:.1f}%;"></div>
                                        <span class="agent-confidence-label">{conf*100:.1f}% Confidence</span>
                                    </div>
                                    ''',
                                    unsafe_allow_html=True
                                )
                                if sig.get('target_price'):
                                    st.markdown(
                                        f"<div class='agent-target-stop'>"
                                        f"<span style='font-weight:600;'>Target Price:</span> <span style='color:#2E8B57;font-weight:600;'>{currency}{sig['target_price']:.2f} 💰</span>"
                                        f"</div>",
                                        unsafe_allow_html=True
                                    )
                                if sig.get('stop_loss'):
                                    st.markdown(
                                        f"<div class='agent-target-stop'>"
                                        f"<span style='font-weight:600;'>Stop Loss:</span> <span style='color:#d32f2f;font-weight:600;'>{currency}{sig['stop_loss']:.2f} 🚫</span>"
                                        f"</div>",
                                        unsafe_allow_html=True
                                    )
                                st.markdown("<div class='agent-reasoning-title'>Reasoning:</div>", unsafe_allow_html=True)
                                st.markdown(
                                    f"<div class='agent-reasoning-body'>{sig.get('reasoning', 'No reasoning provided')}</div>",
                                    unsafe_allow_html=True
                                )
                            st.markdown("</div>", unsafe_allow_html=True)
            else:
                st.error(f"API Error: {response.status_code}") 