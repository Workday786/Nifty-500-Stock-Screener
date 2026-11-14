import streamlit as st
import pandas as pd
import yfinance as yf
import time, io, requests
from datetime import datetime

st.set_page_config(layout="wide", page_title="Nifty 500 — 1-Min Scanner")
st.title("⚡ Nifty 500 — 1 Minute % Change Scanner")
st.caption(f"Live scan · Auto-refresh every 60s · Last updated: {datetime.now().strftime('%H:%M:%S')}")

# ---- 1. Get Nifty 500 symbol list ----
@st.cache_data(ttl=86400)  # cache symbol list for 1 day
def get_nifty500_symbols():
    url = "https://archives.nseindia.com/content/indices/ind_nifty500list.csv"
    headers = {"User-Agent": "Mozilla/5.0"}
    csv = requests.get(url, headers=headers, timeout=15).content
    df = pd.read_csv(io.BytesIO(csv))
    return [s.strip() + ".NS" for s in df["Symbol"].tolist()]

symbols = get_nifty500_symbols()
st.sidebar.info(f"Tracking {len(symbols)} stocks")

# ---- 2. Fetch quotes in batches ----
def fetch_prices(symbols):
    data = {}
    batch = 100
    for i in range(0, len(symbols), batch):
        chunk = symbols[i:i+batch]
        try:
            tickers = yf.Tickers(" ".join(chunk))
            for sym in chunk:
                try:
                    fast = tickers.tickers[sym].fast_info
                    data[sym] = fast["last_price"]
                except Exception:
                    pass
        except Exception:
            pass
    return data

# ---- 3. Store previous price to compute 1-min change ----
if "prev" not in st.session_state:
    st.session_state.prev = {}
    st.session_state.prev_time = None

prices = fetch_prices(symbols)

rows = []
for sym, price in prices.items():
    prev_price = st.session_state.prev.get(sym)
    change_1m = None
    if prev_price and prev_price > 0 and price:
        change_1m = round((price - prev_price) / prev_price * 100, 2)
    rows.append({
        "Symbol": sym.replace(".NS", ""),
        "LTP": price,
        "1-Min % Change": change_1m,
    })

# Save current prices for next minute's comparison
st.session_state.prev = prices
df = pd.DataFrame(rows)
df = df.sort_values("1-Min % Change", ascending=False, na_position="last")

# ---- 4. Display with color coding ----
st.dataframe(
    df,
    height=720,
    use_container_width=True,
    hide_index=True,
    column_config={
        "1-Min % Change": st.column_config.NumberColumn(format="%.2f%%"),
        "LTP": st.column_config.NumberColumn(format="₹%.2f"),
    },
)

# Color highlight via simple top/bottom summary
c1, c2, c3 = st.columns(3)
gainers = df[df["1-Min % Change"] > 0]
losers = df[df["1-Min % Change"] < 0]
c1.success(f"🟢 Rising: {len(gainers)}")
c2.error(f"🔴 Falling: {len(losers)}")
c3.info(f"⚪ Flat/No data: {len(df) - len(gainers) - len(losers)}")

# ---- 5. Auto-refresh every 60 seconds ----
time.sleep(60)
st.rerun()
