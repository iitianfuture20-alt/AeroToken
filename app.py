import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st
from statsmodels.tsa.arima.model import ARIMA
from datetime import datetime, timedelta
import hashlib

st.set_page_config(page_title="CleanToken", page_icon="🌿", layout="wide")
st.title("🌿 CleanToken: Breathe Easy, Earn Tokens")
st.sidebar.header("Quick Nav")
page = st.sidebar.selectbox("Choose a Feature", ["Pollution Dashboard", "AI Forecast", "Earn Tokens", "Redeem Perks"])

@st.cache_data
def load_data():
    np.random.seed(42)
    dates = pd.date_range(start='2025-01-01', periods=30, freq='D')
    areas = ['Downtown', 'Suburbs', 'Industrial']
    data = []
    for area in areas:
        base_level = {'Downtown': 80, 'Suburbs': 50, 'Industrial': 120}[area]
        pm25 = base_level + np.cumsum(np.random.randn(30) * 10)
        co2 = 400 + np.cumsum(np.random.randn(30) * 20)
        for d, p, c in zip(dates, pm25, co2):
            data.append({'Date': d, 'Area': area, 'PM2.5': max(0, p), 'CO2': c})
    return pd.DataFrame(data)

df = load_data()

def forecast_pm25(area_data):
    pm_series = area_data['PM2.5'].values
    if len(pm_series) < 5:
        return np.mean(pm_series)
    model = ARIMA(pm_series, order=(1,1,1))
    model_fit = model.fit()
    forecast = model_fit.forecast(steps=1)
    return float(forecast.iloc[0]) if hasattr(forecast, 'iloc') else float(forecast[0])

def calculate_tokens(action, impact):
    base_tokens = impact * 10
    tx_hash = hashlib.sha256(f"{action}_{impact}_{datetime.now()}".encode()).hexdigest()[:10]
    return base_tokens, tx_hash

perks = {
    "Free Water (1L)": 10,
    "Coffee Discount": 20,
    "Bus Pass Extension": 50,
    "Grocery Voucher": 100,
    "Cashback ($5)": 200
}

if page == "Pollution Dashboard":
    st.header("🗺️ Real-Time Pollution Trends")
    col1, col2 = st.columns(2)
    with col1:
        selected_area = st.selectbox("Select Area", df['Area'].unique())
        area_df = df[df['Area'] == selected_area].set_index('Date')
        st.subheader(f"PM2.5 Levels in {selected_area}")
        fig, ax = plt.subplots()
        area_df['PM2.5'].plot(ax=ax, color='orange')
        ax.set_ylabel('PM2.5 (µg/m³)')
        ax.set_title(f"{selected_area} Air Quality")
        st.pyplot(fig)
    with col2:
        st.subheader("All Areas Overview")
        fig2, ax2 = plt.subplots()
        for area in df['Area'].unique():
            sub_df = df[df['Area'] == area].set_index('Date')
            sub_df['PM2.5'].plot(ax=ax2, label=area)
        ax2.set_ylabel('PM2.5 (µg/m³)')
        ax2.legend()
        st.pyplot(fig2)
    st.caption("Data simulated; integrate OpenAQ API for live feeds.")

elif page == "AI Forecast":
    st.header("🔮 Tomorrow's Air Quality Prediction")
    selected_area = st.selectbox("Forecast for Area", df['Area'].unique())
    area_df = df[df['Area'] == selected_area]
    current_avg = area_df['PM2.5'].mean()
    forecast_val = forecast_pm25(area_df)
    st.metric("Current Average PM2.5", f"{current_avg:.1f} µg/m³", f"{forecast_val:.1f} µg/m³")
    if forecast_val > 100:
        st.warning("🚨 High pollution alert! Double tokens for actions today.")
    else:
        st.success("✅ Good air tomorrow—keep it up!")

elif page == "Earn Tokens":
    st.header("💚 Log Your Eco-Action & Earn CAT")
    user_name = st.text_input("Your Name", "EcoWarrior")
    action = st.text_input("Action (e.g., 'Planted 3 trees')")
    impact = st.slider("Impact Level (1-10)", 1, 10, 3)
    if st.button("Submit & Mint Tokens"):
        tokens, tx_hash = calculate_tokens(action, impact)
        st.session_state.setdefault('wallet', 0)
        st.session_state.wallet += tokens
        st.success(f"🎉 {tokens} CAT minted to your wallet! TX: {tx_hash}")
        st.balloons()
    st.info(f"Current Wallet: {st.session_state.get('wallet', 0)} CAT")

elif page == "Redeem Perks":
    st.header("🛒 Spend Your CAT on Rewards")
    wallet = st.session_state.get('wallet', 0)
    st.metric("Your CAT Balance", wallet)
    selected_perk = st.selectbox("Choose a Perk", list(perks.keys()))
    cost = perks[selected_perk]
    if wallet >= cost:
        if st.button(f"Redeem {selected_perk} ({cost} CAT)"):
            st.session_state.wallet -= cost
            st.success(f"✅ Redeemed! Enjoy your {selected_perk}. New balance: {st.session_state.wallet} CAT")
    else:
        st.error(f"⏳ Need {cost - wallet} more CAT. Go earn some!")

st.sidebar.markdown("---")
st.sidebar.caption("Built with ❤️ for a cleaner planet. Next: Add blockchain & mobile!")
