import pandas as pd
import plotly.graph_objects as go
import streamlit as st

st.set_page_config(page_title="Fixed Income Dashboard", page_icon="📈", layout="wide")

POSITIONS = pd.DataFrame(
    [
        ("U.S. Treasury 4.125 2031", "Government", 4.28, 18.6, 5.1),
        ("Microsoft 3.95 2030", "Corporate", 4.62, 9.8, 4.2),
        ("JPMorgan 4.60 2033", "Financial", 5.03, 8.1, 5.9),
        ("Apple 4.45 2034", "Corporate", 4.89, 7.4, 6.3),
        ("Vanguard Short-Term Bond ETF", "ETF", 4.55, 6.2, 2.4),
    ],
    columns=["Security", "Sector", "YTM (%)", "Weight (%)", "Duration (yrs)"],
)
SWITCHES = pd.DataFrame(
    [
        ("Microsoft 3.95 2030", "Verizon 4.75 2031", 38, 0.7, 0, 1),
        ("U.S. Treasury 4.125 2031", "JPMorgan 4.60 2033", 74, 1.2, 1, 1),
        ("Apple 4.45 2034", "Ford Motor Credit 5.35 2031", 92, -0.4, 2, 2),
        ("JPMorgan 4.60 2033", "Bank of America 5.10 2034", 31, 1.7, 0, 1),
        ("Microsoft 3.95 2030", "AT&T 5.20 2033", 67, 1.5, 1, 2),
    ],
    columns=["From", "To", "Pickup (bps)", "Excess duration", "Rank downgrade", "Rating notches"],
)

CURVE = pd.DataFrame(
    {"Maturity": ["3M", "2Y", "5Y", "10Y", "20Y", "30Y"], "Yield": [4.18, 4.35, 4.44, 4.58, 4.67, 4.72]}
)

st.title("Fixed Income Dashboard")
st.caption("Illustrative data · USD investment-grade portfolio")

with st.sidebar:
    st.header("Portfolio controls")
    benchmark = st.selectbox("Benchmark", ["Bloomberg US Aggregate", "US Treasury", "Custom"], index=0)
    shock = st.slider("Parallel rate shock (bps)", -100, 100, 0, 5)
    st.caption(f"Comparing with {benchmark}")

market_value = 12_480_000
portfolio_duration = (POSITIONS["Weight (%)"] * POSITIONS["Duration (yrs)"]).sum() / POSITIONS["Weight (%)"].sum()
dv01 = market_value * portfolio_duration * 0.0001
estimated_pnl = -dv01 * shock

a, b, c, d = st.columns(4)
a.metric("Market value", f"${market_value / 1_000_000:.2f}m", "+0.32% today")
b.metric("Yield to maturity", "4.71%", "+6 bps MTD")
c.metric("Modified duration", f"{portfolio_duration:.2f} years")
d.metric("Rate-shock P&L", f"${estimated_pnl:,.0f}", f"{shock:+d} bps")

left, right = st.columns([1.25, 1])
with left:
    st.subheader("U.S. Treasury curve")
    shocked_curve = CURVE.assign(Yield=CURVE["Yield"] + shock / 100)
    fig = go.Figure(go.Scatter(x=shocked_curve["Maturity"], y=shocked_curve["Yield"], mode="lines+markers", line={"color": "#16a085", "width": 3}))
    fig.update_layout(height=320, margin={"l": 0, "r": 0, "t": 10, "b": 0}, yaxis_title="Yield (%)", template="plotly_white")
    st.plotly_chart(fig, use_container_width=True)
with right:
    st.subheader("Largest positions")
    st.dataframe(POSITIONS[["Security", "YTM (%)", "Weight (%)"]], hide_index=True, use_container_width=True)

st.subheader("Holdings detail")
st.dataframe(POSITIONS, hide_index=True, use_container_width=True)

st.subheader("Switch score — pickup adjusted for risk")
st.caption("A quick screen, not an investment recommendation. Higher scores mean more spread pickup after simple risk penalties.")

with st.expander("Scoring assumptions", expanded=False):
    st.write("Net score = spread pickup − (excess duration × duration penalty) − (payment-rank downgrade × rank penalty) − (rating notches × rating penalty).")
    duration_penalty = st.slider("Duration penalty (bps per excess year)", 0, 20, 8)
    rank_penalty = st.slider("Payment-rank penalty (bps per notch)", 0, 40, 15)
    rating_penalty = st.slider("Rating penalty (bps per notch)", 0, 30, 10)

switches = SWITCHES.copy()
switches["Duration penalty"] = switches["Excess duration"].clip(lower=0) * duration_penalty
switches["Rank penalty"] = switches["Rank downgrade"] * rank_penalty
switches["Rating penalty"] = switches["Rating notches"] * rating_penalty
switches["Net score (bps)"] = switches["Pickup (bps)"] - switches[["Duration penalty", "Rank penalty", "Rating penalty"]].sum(axis=1)
switches = switches.sort_values("Net score (bps)", ascending=False).reset_index(drop=True)

best = switches.iloc[0]
st.info(f"Best illustrative switch: **{best['From']} → {best['To']}** · **{best['Net score (bps)']:.0f} bps net score** after risk penalties.")
st.dataframe(
    switches[["From", "To", "Pickup (bps)", "Excess duration", "Rank downgrade", "Rating notches", "Net score (bps)"]],
    hide_index=True,
    use_container_width=True,
)

