import io
import time
from datetime import datetime
from zoneinfo import ZoneInfo

import pandas as pd
import requests
import streamlit as st
import yfinance as yf

st.set_page_config(
    layout="wide",
    page_title="Nifty 500 — 1-Min Scanner",
    initial_sidebar_state="collapsed",
)

# Compact mobile-friendly padding
st.markdown(
    """
    <style>
        .block-container { padding-top: 1rem; padding-bottom: 1rem; padding-left: 0.75rem; padding-right: 0.75rem; }
        h1 { font-size: 1.45rem !important; }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("⚡ Nifty 500 — 1-Min Scanner")

# ---- 1. Get Nifty 500 symbol list ----
@st.cache_data(ttl=86400)
def get_nifty500_symbols():
    url = "https://archives.nseindia.com/content/indices/ind_nifty500list.csv"
    headers = {"User-Agent": "Mozilla/5.0"}
    csv_bytes = requests.get(url, headers=headers, timeout=15).content
    df = pd.read_csv(io.BytesIO(csv_bytes))
    # Filter out dummy/placeholder symbols
    df = df[~df["Symbol"].str.startswith("DUMMY", na=False)]
    return [s.strip() + ".NS" for s in df["Symbol"].dropna().tolist()]


# ---- 2. Bulk download latest prices (much faster than fast_info loop) ----
@st.cache_data(ttl=45, show_spinner=False)
def fetch_bulk_quotes(symbols):
    # Download last 2 daily bars in bulk to get Prev Close & Latest Price in 1-2 requests
    raw = yf.download(
        tickers=symbols,
        period="2d",
        interval="1d",
        group_by="ticker",
        threads=True,
        progress=False,
    )
    quotes = {}
    for sym in symbols:
        try:
            closes = raw[sym]["Close"].dropna()
            if len(closes) >= 2:
                quotes[sym] = {
                    "prev_close": float(closes.iloc[-2]),
                    "ltp": float(closes.iloc[-1]),
                }
            elif len(closes) == 1:
                quotes[sym] = {
                    "prev_close": None,
                    "ltp": float(closes.iloc[-1]),
                }
        except Exception:
            pass
    return quotes


symbols = get_nifty500_symbols()

if "prev_prices" not in st.session_state:
    st.session_state.prev_prices = {}

# ---- 3. Auto-refreshing live fragment (keeps mobile UI responsive) ----
@st.fragment(run_every=60)
def render_scanner():
    ist_now = datetime.now(ZoneInfo("Asia/Kolkata")).strftime("%H:%M:%S IST")
    
    # Mobile-friendly top controls
    sort_by = st.radio(
        "Sort by",
        ["1-Min % (Top Movers)", "1-Min % (Gainers)", "1-Min % (Losers)", "1-Day %"],
        horizontal=True,
        label_visibility="collapsed",
    )

    with st.spinner("Scanning Nifty 500..."):
        quotes = fetch_bulk_quotes(symbols)

    rows = []
    for sym, q in quotes.items():
        ltp = q["ltp"]
        prev_close = q["prev_close"]

        change_1d = None
        if prev_close and prev_close > 0 and ltp:
            change_1d = round((ltp - prev_close) / prev_close * 100, 2)

        prev_price = st.session_state.prev_prices.get(sym)
        change_1m = None
        if prev_price and prev_price > 0 and ltp:
            change_1m = round((ltp - prev_price) / prev_price * 100, 2)

        rows.append({
            "Symbol": sym.replace(".NS", ""),
            "LTP": round(ltp, 2),
            "1m %": change_1m,
            "1d %": change_1d,
            "abs_1m": abs(change_1m) if change_1m is not None else -1,
        })

    # Update snapshot for next 60s cycle
    st.session_state.prev_prices = {sym: q["ltp"] for sym, q in quotes.items()}

    df = pd.DataFrame(rows)

    if sort_by == "1-Min % (Top Movers)":
        df = df.sort_values(["abs_1m", "1d %"], ascending=[False, False], na_position="last")
    elif sort_by == "1-Min % (Gainers)":
        df = df.sort_values("1m %", ascending=False, na_position="last")
    elif sort_by == "1-Min % (Losers)":
        df = df.sort_values("1m %", ascending=True, na_position="last")
    else:
        df = df.sort_values("1d %", ascending=False, na_position="last")

    display_df = df[["Symbol", "LTP", "1m %", "1d %"]]

    st.caption(f"Updated: {ist_now} · Tracked: {len(display_df)}/{len(symbols)}")

    st.dataframe(
        display_df,
        height=540,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Symbol": st.column_config.TextColumn(width="small"),
            "LTP": st.column_config.NumberColumn(format="₹%.2f", width="small"),
            "1m %": st.column_config.NumberColumn(format="%.2f%%", width="small"),
            "1d %": st.column_config.NumberColumn(format="%.2f%%", width="small"),
        },
    )

    gainers = int((df["1d %"] > 0).sum())
    losers = int((df["1d %"] < 0).sum())
    flat = len(df) - gainers - losers
    st.markdown(f"🟢 **Up:** {gainers} &nbsp;|&nbsp; 🔴 **Down:** {losers} &nbsp;|&nbsp; ⚪ **Flat:** {flat}")


render_scanner()
