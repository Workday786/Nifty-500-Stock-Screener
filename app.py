import io, os
from datetime import datetime
from zoneinfo import ZoneInfo
import pandas as pd
import requests
import streamlit as st
import yfinance as yf

st.set_page_config(layout="wide", page_title="Nifty 500 Scanner", initial_sidebar_state="collapsed")

st.markdown("""
<style>
.block-container { padding: 3.2rem 0.75rem 1rem 0.75rem; }
.tv-header { display: flex; justify-content: space-between; align-items: center; background: #1E222D; border: 1px solid #2A2E39; border-radius: 6px; padding: 10px 14px; margin-bottom: 10px; }
.tv-title { font-size: 1.1rem; font-weight: 700; color: #FFFFFF; }
.tv-live { background: rgba(8,153,129,0.18); color: #089981; border: 1px solid #089981; padding: 3px 8px; border-radius: 4px; font-size: 0.72rem; font-weight: 600; white-space: nowrap; }
.tv-closed { background: rgba(242,54,69,0.18); color: #F23645; border: 1px solid #F23645; padding: 3px 8px; border-radius: 4px; font-size: 0.72rem; font-weight: 600; white-space: nowrap; }
</style>
""", unsafe_allow_html=True)

@st.cache_data(ttl=86400)
def get_nifty500_symbols():
    df = None
    # 1. Check local CSV in repo
    base_dir = os.path.dirname(os.path.abspath(__file__))
    csv_path = os.path.join(base_dir, "ind_nifty500list.csv")
    if os.path.exists(csv_path):
        df = pd.read_csv(csv_path, encoding="utf-8-sig")

    # 2. Original NSE archives URL
    if df is None or "Symbol" not in [str(c).strip() for c in df.columns]:
        try:
            url = "https://nseindia.com"
            headers = {"User-Agent": "Mozilla/5.0"}
            csv_bytes = requests.get(url, headers=headers, timeout=15).content
            df = pd.read_csv(io.BytesIO(csv_bytes))
        except Exception:
            pass

    # 3. Full raw GitHub CSV URL
    if df is None or "Symbol" not in [str(c).strip() for c in df.columns]:
        gh_url = "https://githubusercontent.com"
        csv_bytes = requests.get(gh_url, timeout=15).content
        df = pd.read_csv(io.BytesIO(csv_bytes))

    df.columns = [str(c).strip() for c in df.columns]
    syms = [str(s).strip() for s in df["Symbol"].dropna().tolist()]
    syms = [s for s in syms if s and not s.startswith("DUMMY")]
    return [s + ".NS" for s in syms]

@st.cache_data(ttl=45, show_spinner=False)
def fetch_bulk_quotes(syms):
    raw = yf.download(tickers=syms, period="5d", interval="1d", group_by="ticker", threads=True, progress=False)
    quotes = {}
    for s in syms:
        try:
            c = raw[s]["Close"].dropna()
            if len(c) >= 2:
                quotes[s] = {"prev": float(c.iloc[-2]), "ltp": float(c.iloc[-1])}
            elif len(c) == 1:
                quotes[s] = {"prev": None, "ltp": float(c.iloc[-1])}
        except Exception:
            pass
    return quotes

yf_syms = get_nifty500_symbols()
if "prev_px" not in st.session_state:
    st.session_state.prev_px = {}

def color_pct(v):
    if pd.isna(v) or v == 0:
        return "color: #787B86;"
    return "color: #089981; font-weight: 600;" if v > 0 else "color: #F23645; font-weight: 600;"

@st.fragment(run_every=60)
def render_scanner():
    now = datetime.now(ZoneInfo("Asia/Kolkata"))
    is_open = (now.weekday() < 5) and (555 <= now.hour * 60 + now.minute <= 930)
    badge = '<span class="tv-live">● NSE LIVE</span>' if is_open else '<span class="tv-closed">● MARKET CLOSED</span>'

    with st.spinner("Syncing market feed..."):
        quotes = fetch_bulk_quotes(yf_syms)

    st.markdown(f'<div class="tv-header"><div><div class="tv-title">NIFTY 500 SCREENER</div><div style="font-size:0.72rem;color:#787B86;">Loaded: {len(quotes)}/{len(yf_syms)} · {now.strftime("%H:%M:%S IST")}</div></div>{badge}</div>', unsafe_allow_html=True)

    rows = []
    for s, q in quotes.items():
        ltp, prev = q["ltp"], q["prev"]
        c1d = round((ltp - prev) / prev * 100, 2) if (prev and prev > 0 and ltp) else None
        p1m = st.session_state.prev_px.get(s)
        c1m = round((ltp - p1m) / p1m * 100, 2) if (p1m and p1m > 0 and ltp) else None
        rows.append({"Symbol": s.replace(".NS", ""), "LTP": round(ltp, 2), "1m %": c1m, "1d %": c1d})

    st.session_state.prev_px = {s: q["ltp"] for s, q in quotes.items()}
    df = pd.DataFrame(rows)

    q_txt = st.text_input("Search", placeholder="🔍 Search ticker (e.g. RELIANCE)...", label_visibility="collapsed")
    sort_by = st.radio("Filter", ["All", "1m Gainers", "1m Losers"], horizontal=True, label_visibility="collapsed")

    if df.empty:
        st.warning("No market data returned yet. Retrying on next cycle...")
        return

    if q_txt:
        df = df[df["Symbol"].str.contains(q_txt.strip().upper(), na=False)]

    if sort_by == "1m Gainers":
        df = df[df["1m %"].notna() & (df["1m %"] > 0)].sort_values("1m %", ascending=False)
    elif sort_by == "1m Losers":
        df = df[df["1m %"].notna() & (df["1m %"] < 0)].sort_values("1m %", ascending=True)
    else:
        df = df.sort_values("1d %", ascending=False, na_position="last")

    styled = df[["Symbol", "LTP", "1m %", "1d %"]].style.map(color_pct, subset=["1m %", "1d %"]).format({"LTP": "₹{:.2f}", "1m %": "{:+.2f}%", "1d %": "{:+.2f}%"}, na_rep="—")
    st.dataframe(styled, height=580, use_container_width=True, hide_index=True)

render_scanner()
