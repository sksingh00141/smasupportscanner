import streamlit as st
import pandas as pd
import yfinance as yf
import pyotp
from smartapi import SmartConnect
import json

# Load credentials
with open("config.json") as f:
    creds = json.load(f)

API_KEY = creds["api_key"]
CLIENT_ID = creds["client_id"]
TOTP_SECRET = creds["totp_secret"]

# Generate TOTP
totp = pyotp.TOTP(TOTP_SECRET).now()

# SmartAPI Login
try:
    smartApi = SmartConnect(api_key=API_KEY)
    data = smartApi.generateSession(CLIENT_ID, totp=totp)
    st.success("✅ SmartAPI Login Successful!")
except Exception as e:
    st.error(f"SmartAPI Login Failed: {e}")

st.title("📈 Intraday Bounce Scanner")

symbol = st.text_input("Enter Stock Symbol (e.g. DIXON.NS):", "DIXON.NS")
tf = st.selectbox("Select Timeframe:", ["15m", "30m", "1h"])

if st.button("🔍 Scan"):
    df = yf.download(symbol, period="1mo", interval=tf)
    df["SMA20"] = df["Close"].rolling(20).mean()
    df["SMA50"] = df["Close"].rolling(50).mean()

    last_close = df["Close"].iloc[-1]
    last_sma20 = df["SMA20"].iloc[-1]
    last_sma50 = df["SMA50"].iloc[-1]

    st.write("🔍 **Last Candle Details:**")
    st.write(df.tail(10))

    if last_close >= last_sma20 or last_close >= last_sma50:
        st.success("✅ Price is at or above SMA support")
    else:
        st.warning("⚠️ Price is below both SMAs")
