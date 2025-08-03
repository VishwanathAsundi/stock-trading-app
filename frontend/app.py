import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

st.set_page_config(
    page_title="AI Stock Analyzer",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Custom CSS for a more interesting UI, especially agent signals and reasoning ---
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
/* --- Highlight and enlarge Sentiment Agent and Technical Agent titles --- */
.agent-title-highlight {
    font-size: 2.1rem !important;
    font-weight: 900 !important;
    color: #fff !important;
    background: linear-gradient(90deg, #0072C6 0%, #2E8B57 100%);
    padding: 8px 28px 8px 18px;
    border-radius: 12px;
    box-shadow: 0 2px 12px #b2d7ff55;
    margin-bottom: 12px;
    margin-top: 0;
    display: inline-block;
    letter-spacing: 1.2px;
    font-family: 'Montserrat', 'Segoe UI', 'Roboto', sans-serif;
    border-left: 8px solid #ff9800;
}
.agent-title-highlight.sentiment {
    background: linear-gradient(90deg, #ff9800 0%, #0072C6 100%);
    color: #fff !important;
    border-left: 8px solid #0072C6;
}
.agent-title-highlight.technical {
    background: linear-gradient(90deg, #2E8B57 0%, #0072C6 100%);
    color: #fff !important;
    border-left: 8px solid #2E8B57;
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
    letter-spacing: 0.5px;
    display: flex;
    align-items: center;
    gap: 7px;
}
.agent-reasoning-title .reasoning-icon {
    font-size: 1.3rem;
    margin-right: 2px;
}
.agent-reasoning-body {
    font-size: 1.08rem;
    color: #222;
    font-family: 'Segoe UI', 'Roboto', 'Helvetica Neue', Arial, 'Liberation Sans', sans-serif;
    background: linear-gradient(100deg, #e0eafc 60%, #f7fafc 100%);
    border-radius: 10px;
    padding: 14px 18px 14px 18px;
    margin-bottom: 0;
    margin-top: 4px;
    box-shadow: 0 2px 8px #b2d7ff33;
    border-left: 5px solid #2E8B57;
    position: relative;
    transition: box-shadow 0.3s;
    min-height: 48px;
}
.agent-reasoning-body:before {
    content: "💡";
    position: absolute;
    left: -32px;
    top: 12px;
    font-size: 1.5rem;
    opacity: 0.85;
}
.agent-reasoning-body strong, .agent-reasoning-body b {
    color: #0072C6;
}
.agent-reasoning-body em, .agent-reasoning-body i {
    color: #2E8B57;
}
.agent-reasoning-body code {
    background: #e0eafc;
    color: #d32f2f;
    border-radius: 4px;
    padding: 2px 6px;
    font-size: 0.98em;
}
.agent-reasoning-body ul, .agent-reasoning-body ol {
    margin-left: 1.2em;
    margin-bottom: 0;
}
.agent-reasoning-body a {
    color: #0072C6;
    text-decoration: underline;
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
                            # Calculate moving averages for more impressive chart
                            hist['MA5'] = hist['Close'].rolling(window=5).mean()
                            hist['MA10'] = hist['Close'].rolling(window=10).mean()
                            # Create candlestick chart with moving averages and volume
                            fig = go.Figure()
                            # Candlestick
                            fig.add_trace(go.Candlestick(
                                x=hist.index,
                                open=hist['Open'],
                                high=hist['High'],
                                low=hist['Low'],
                                close=hist['Close'],
                                name='Price',
                                increasing_line_color='#2E8B57',
                                decreasing_line_color='#d32f2f',
                                showlegend=True
                            ))
                            # MA5
                            fig.add_trace(go.Scatter(
                                x=hist.index, y=hist['MA5'],
                                mode='lines',
                                line=dict(color='#0072C6', width=2, dash='dot'),
                                name='MA 5',
                                hovertemplate='MA 5: %{y:.2f}<extra></extra>'
                            ))
                            # MA10
                            fig.add_trace(go.Scatter(
                                x=hist.index, y=hist['MA10'],
                                mode='lines',
                                line=dict(color='#ff9800', width=2, dash='dash'),
                                name='MA 10',
                                hovertemplate='MA 10: %{y:.2f}<extra></extra>'
                            ))
                            # Volume as bar chart (secondary y)
                            fig.add_trace(go.Bar(
                                x=hist.index, y=hist['Volume'],
                                name='Volume',
                                marker_color='rgba(44, 130, 201, 0.25)',
                                yaxis='y2',
                                opacity=0.5,
                                hovertemplate='Volume: %{y}<extra></extra>'
                            ))
                            # Layout
                            fig.update_layout(
                                title={
                                    'text': f"📈 <b>{symbol.upper()} Price Chart (1 Month)</b>",
                                    'x':0.5,
                                    'xanchor': 'center',
                                    'font': dict(size=22, color="#0072C6", family="Montserrat,Segoe UI,Roboto,sans-serif")
                                },
                                xaxis=dict(
                                    title="Date",
                                    rangeslider=dict(visible=False),
                                    showgrid=True,
                                    gridcolor="#e0eafc",
                                    tickformat="%b %d",
                                    tickfont=dict(size=12, color="#232526")
                                ),
                                yaxis=dict(
                                    title="Price",
                                    showgrid=True,
                                    gridcolor="#e0eafc",
                                    tickfont=dict(size=12, color="#232526")
                                ),
                                yaxis2=dict(
                                    title="Volume",
                                    overlaying='y',
                                    side='right',
                                    showgrid=False,
                                    tickfont=dict(size=11, color="#0072C6")
                                ),
                                legend=dict(
                                    orientation="h",
                                    yanchor="bottom",
                                    y=1.02,
                                    xanchor="right",
                                    x=1,
                                    font=dict(size=13, family="Montserrat,Segoe UI,Roboto,sans-serif")
                                ),
                                plot_bgcolor="#f7fafc",
                                paper_bgcolor="#f7fafc",
                                margin=dict(l=10, r=10, t=60, b=10),
                                hovermode="x unified",
                                height=480
                            )
                            # Add annotation for current price
                            last_close = hist['Close'][-1]
                            fig.add_hline(
                                y=last_close,
                                line_dash="dot",
                                line_color="#2E8B57",
                                annotation_text=f"Current: {currency}{last_close:.2f}",
                                annotation_position="top right",
                                annotation_font_color="#2E8B57",
                                annotation_font_size=14
                            )
                            st.plotly_chart(fig, use_container_width=True)
                    except Exception as ex:
                        st.warning("Could not load advanced chart. Showing basic chart.")
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
                        # --- Highlight Sentiment Agent and Technical Agent titles ---
                        if agent.lower() == "sentiment":
                            expander_label = f"📰 Sentiment Agent"
                        elif agent.lower() == "technical":
                            expander_label = f"📊 Technical Agent"
                        elif agent.lower() == "risk":
                            expander_label = f"⚠️ Risk Management Agent"
                        else:
                            expander_label = f"{icon} {agent.title()} Agent"
                        # Streamlit's st.expander does not support HTML in the label, so we use plain text
                        with st.expander(expander_label, expanded=True):
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
                                # --- Attractive Reasoning Section ---
                                st.markdown(
                                    "<div class='agent-reasoning-title'><span class='reasoning-icon'>💡</span>Reasoning:</div>",
                                    unsafe_allow_html=True
                                )
                                reasoning = sig.get('reasoning', 'No reasoning provided')
                                # Optionally, you could add markdown rendering for lists, bold, etc.
                                st.markdown(
                                    f"<div class='agent-reasoning-body'>{reasoning}</div>",
                                    unsafe_allow_html=True
                                )
                            st.markdown("</div>", unsafe_allow_html=True)
            else:
                st.error(f"API Error: {response.status_code}") 