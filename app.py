import io
from datetime import datetime
from zoneinfo import ZoneInfo

import pandas as pd
import requests
import streamlit as st
import yfinance as yf

st.set_page_config(
    layout="wide",
    page_title="Nifty 500 — TV Dark Scanner",
    initial_sidebar_state="collapsed",
)

# ---- TradingView Dark Theme Custom CSS ----
st.markdown(
    """
    <style>
        /* Main container & typography */
        .block-container {
            padding-top: 0.8rem;
            padding-bottom: 1rem;
            padding-left: 0.75rem;
            padding-right: 0.75rem;
        }
        header[data-testid="stHeader"] {
            background-color: #131722;
        }
        /* Top TradingView Header Bar */
        .tv-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            background-color: #1E222D;
            border: 1px solid #2A2E39;
            border-radius: 6px;
            padding: 10px 14px;
            margin-bottom: 10px;
        }
        .tv-title {
            font-size: 1.15rem;
            font-weight: 700;
            color: #FFFFFF;
            letter-spacing: 0.3px;
        }
        .tv-badge-live {
            background-color: rgba(8, 153, 129, 0.18);
            color: #089981;
            border: 1px solid #089981;
            padding: 2px 8px;
            border-radius: 4px;
            font-size: 0.72rem;
            font-weight: 600;
        }
        .tv-badge-closed {
            background-color: rgba(242, 54, 69, 0.18);
            color: #F23645;
            border: 1px solid #F23645;
            padding: 2px 8px;
            border-radius: 4px;
            font-size: 0.72rem;
            font-weight: 600;
        }
        /* Metric Cards */
        .tv-card-grid {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 8px;
            margin-bottom: 10px;
        }
        .tv-card {
            background-color: #1E222D;
            border: 1px solid #2A2E39;
            border-radius: 6px;
            padding: 8px 10px;
        }
        .tv-card-label {
            font-size: 0.7rem;
            color: #787B86;
            text-transform: uppercase;
            font-weight: 600;
        }
        .tv-card-val {
            font-size: 0.95rem;
            font-weight: 700;
            color: #D1D4DC;
            margin-top: 2px;
        }
        .tv-green { color: #089981 !important; }
        .tv-red { color: #F23645 !important; }
        /* Radio Pills Styling */
        div[role="radiogroup"] {
            gap: 6px;
        }
        div[role="radiogroup"] label {
            background-color: #1E222D;
            border: 1px solid #2A2E39;
            border-radius: 4px;
            padding: 4px 10px;
            font-size: 0.8rem;
        }
    </style>
    """,
    unsafe_allow_html=True,
)


# ---- 1. Fetch Nifty 500 Symbols + Industry ----
@st.cache_data(ttl=86400)
def get_nifty500_meta():
    url = "https://nseindia.com"
    headers = {"User-Agent": "Mozilla/5.0"}
    csv_bytes = requests.get(url, headers=headers, timeout=15).content
    df = pd.read_csv(io.BytesIO(csv_bytes))
    df = df[~df["Symbol"].str.startswith("DUMMY", na=False)].dropna(subset=["Symbol"])
    df["Symbol"] = df["Symbol"].str.strip()
    df["YF_Symbol"] = df["Symbol"] + ".NS"
    return df[["Symbol", "YF_Symbol", "Industry"]]


# ---- 2. Bulk Download Quotes ----
@st.cache_data(ttl=45, show_spinner=False)
def fetch_bulk_quotes(yf_symbols):
    raw = yf.download(
        tickers=yf_symbols,
        period="2d",
        interval="1d",
        group_by="ticker",
        threads=True,
        progress=False,
    )
    quotes = {}
    for sym in yf_symbols:
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


meta_df = get_nifty500_meta()
yf_symbols = meta_df["YF_Symbol"].tolist()
industry_map = dict(zip(meta_df["YF_Symbol"], meta_df["Industry"]))

if "prev_prices" not in st.session_state:
    st.session_state.prev_prices = {}


def is_nse_market_open(now_ist: datetime) -> bool:
    if now_ist.weekday() >= 5:  # Sat/Sun
        return False
    mins = now_ist.hour * 60 + now_ist.minute
    return (9 * 60 + 15) <= mins <= (15 * 60 + 30)


def color_pct(val):
    if pd.isna(val) or val == 0:
        return "color: #787B86;"
    return "color: #089981; font-weight: 600;" if val > 0 else "color: #F23645; font-weight: 600;"


# ---- 3. Auto-Refreshing TradingView Screener Fragment ----
@st.fragment(run_every=60)
def render_scanner():
    now_ist = datetime.now(ZoneInfo("Asia/Kolkata"))
    time_str = now_ist.strftime("%H:%M:%S IST")
    market_open = is_nse_market_open(now_ist)

    badge_html = (
        '<span class="tv-badge-live">● NSE LIVE</span>'
        if market_open
        else '<span class="tv-badge-closed">● MARKET CLOSED</span>'
    )

    st.markdown(
        f"""
        <div class="tv-header">
            <div>
                <div class="tv-title">NIFTY 500 SCREENER</div>
                <div style="font-size:0.72rem; color:#787B86;">1-Min Momentum & Intraday Breadth · {time_str}</div>
            </div>
            {badge_html}
        </div>
        """,
        unsafe_allow_html=True,
    )

    with st.spinner("Syncing market feed..."):
        quotes = fetch_bulk_quotes(yf_symbols)

    rows = []
    for sym, q in quotes.items():
        ltp = q["ltp"]
        prev_close = q["prev_close"]

        change_1d = round((ltp - prev_close) / prev_close * 100, 2) if (prev_close and prev_close > 0 and ltp) else None
        prev_price = st.session_state.prev_prices.get(sym)
        change_1m = round((ltp - prev_price) / prev_price * 100, 2) if (prev_price and prev_price > 0 and ltp) else None

        rows.append({
            "Symbol": sym.replace(".NS", ""),
            "Sector": industry_map.get(sym, "Other"),
            "LTP": round(ltp, 2),
            "1m %": change_1m,
            "1d %": change_1d,
            "abs_1m": abs(change_1m) if change_1m is not None else -1,
        })

    st.session_state.prev_prices = {sym: q["ltp"] for sym, q in quotes.items()}
    df = pd.DataFrame(rows)

    # Summary KPI Strip
    gainers_cnt = int((df["1d %"] > 0).sum())
    losers_cnt = int((df["1d %"] < 0).sum())
    top_gainer_row = df.loc[df["1d %"].idxmax()] if not df["1d %"].isna().all() else None
    top_loser_row = df.loc[df["1d %"].idxmin()] if not df["1d %"].isna().all() else None

    tg_text = f"{top_gainer_row['Symbol']} (+{top_gainer_row['1d %']:.2f}%)" if top_gainer_row is not None else "-"
    tl_text = f"{top_loser_row['Symbol']} ({top_loser_row['1d %']:.2f}%)" if top_loser_row is not None else "-"

    st.markdown(
        f"""
        <div class="tv-card-grid">
            <div class="tv-card">
                <div class="tv-card-label">Adv / Dec</div>
                <div class="tv-card-val"><span class="tv-green">{gainers_cnt}</span> / <span class="tv-red">{losers_cnt}</span></div>
            </div>
            <div class="tv-card">
                <div class="tv-card-label">Top Gainer (1D)</div>
                <div class="tv-card-val tv-green">{tg_text}</div>
            </div>
            <div class="tv-card">
                <div class="tv-card-label">Top Loser (1D)</div>
                <div class="tv-card-val tv-red">{tl_text}</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Filter & Sort Controls
    c_search, c_sector = st.columns([1, 1])
    with c_search:
        search_q = st.text_input("Search Symbol", placeholder="🔍 Search ticker (e.g. RELIANCE)...", label_visibility="collapsed")
    with c_sector:
        sectors = ["All Sectors"] + sorted(df["Sector"].dropna().unique().tolist())
        selected_sector = st.selectbox("Sector", sectors, label_visibility="collapsed")

    sort_by = st.radio(
        "Sort",
        ["🔥 1m Movers", "🚀 1m Gainers", "🔻 1m Losers", "📈 1d Gainers", "📉 1d Losers"],
        horizontal=True,
        label_visibility="collapsed",
    )

    if search_q:
        df = df[df["Symbol"].str.contains(search_q.strip().upper(), na=False)]
    if selected_sector != "All Sectors":
        df = df[df["Sector"] == selected_sector]

    if sort_by == "🔥 1m Movers":
        df = df.sort_values(["abs_1m", "1d %"], ascending=[False, False], na_position="last")
    elif sort_by == "🚀 1m Gainers":
        df = df.sort_values("1m %", ascending=False, na_position="last")
    elif sort_by == "🔻 1m Losers":
        df = df.sort_values("1m %", ascending=True, na_position="last")
    elif sort_by == "📈 1d Gainers":
        df = df.sort_values("1d %", ascending=False, na_position="last")
    else:
        df = df.sort_values("1d %", ascending=True, na_position="last")

    display_df = df[["Symbol", "LTP", "1m %", "1d %", "Sector"]]

    styled_df = (
        display_df.style
        .map(color_pct, subset=["1m %", "1d %"])
        .format({"LTP": "₹{:.2f}", "1m %": "{:+.2f}%", "1d %": "{:+.2f}%"}, na_rep="—")
    )

    st.dataframe(
        styled_df,
        height=540,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Symbol": st.column_config.TextColumn(width="small"),
            "LTP": st.column_config.TextColumn(width="small"),
            "1m %": st.column_config.TextColumn(width="small"),
            "1d %": st.column_config.TextColumn(width="small"),
            "Sector": st.column_config.TextColumn(width="medium"),
        },
    )


render_scanner()
