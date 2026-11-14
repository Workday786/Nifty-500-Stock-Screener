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
.block-container { padding: 0.8rem 0.75rem 1rem 0.75rem; }
header[data-testid="stHeader"] { background-color: #131722; }
.tv-header { display: flex; justify-content: space-between; align-items: center; background: #1E222D; border: 1px solid #2A2E39; border-radius: 6px; padding: 10px 14px; margin-bottom: 10px; }
.tv-title { font-size: 1.15rem; font-weight: 700; color: #FFFFFF; }
.tv-live { background: rgba(8,153,129,0.18); color: #089981; border: 1px solid #089981; padding: 2px 8px; border-radius: 4px; font-size: 0.72rem; font-weight: 600; }
.tv-closed { background: rgba(242,54,69,0.18); color: #F23645; border: 1px solid #F23645; padding: 2px 8px; border-radius: 4px; font-size: 0.72rem; font-weight: 600; }
.tv-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 8px; margin-bottom: 10px; }
.tv-card { background: #1E222D; border: 1px solid #2A2E39; border-radius: 6px; padding: 8px 10px; }
.tv-lbl { font-size: 0.7rem; color: #787B86; text-transform: uppercase; font-weight: 600; }
.tv-val { font-size: 0.92rem; font-weight: 700; color: #D1D4DC; margin-top: 2px; }
.tv-g { color: #089981 !important; }
.tv-r { color: #F23645 !important; }
</style>
""", unsafe_allow_html=True)

@st.cache_data(ttl=86400)
def get_nifty500_meta():
    urls = [
        "https://nseindia.com",
        "https://niftyindices.com",
    ]
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/124.0.0.0", "Referer": "https://nseindia.com"}
    df = None
    if os.path.exists("ind_nifty500list.csv"):
        df = pd.read_csv("ind_nifty500list.csv")
    else:
        for u in urls:
            try:
                r = requests.get(u, headers=headers, timeout=15)
                if r.status_code == 200 and "Symbol" in r.text:
                    df = pd.read_csv(io.StringIO(r.text))
                    break
            except Exception:
                pass
    if df is None:
        fb = ["RELIANCE", "TCS", "HDFCBANK", "ICICIBANK", "INFY", "SBIN", "BHARTIARTL", "LT", "ITC", "AXISBANK"]
        return pd.DataFrame({"Symbol": fb, "YF": [s + ".NS" for s in fb], "Industry": ["Other"] * len(fb)})
    df.columns = [str(c).strip() for c in df.columns]
    df["Symbol"] = df["Symbol"].astype(str).str.strip()
    df = df[~df["Symbol"].str.startswith("DUMMY", na=False)]
    df = df[df["Symbol"].ne("") & df["Symbol"].ne("nan")]
    df["YF"] = df["Symbol"] + ".NS"
    df["Industry"] = df["Industry"].fillna("Other").astype(str).str.strip() if "Industry" in df.columns else "Other"
    return df[["Symbol", "YF", "Industry"]]

@st.cache_data(ttl=45, show_spinner=False)
def fetch_bulk_quotes(syms):
    raw = yf.download(tickers=syms, period="2d", interval="1d", group_by="ticker", threads=True, progress=False)
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

meta = get_nifty500_meta()
yf_syms = meta["YF"].tolist()
sec_map = dict(zip(meta["YF"], meta["Industry"]))
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
    st.markdown(f'<div class="tv-header"><div><div class="tv-title">NIFTY 500 SCREENER</div><div style="font-size:0.72rem;color:#787B86;">1-Min Momentum · {now.strftime("%H:%M:%S IST")}</div></div>{badge}</div>', unsafe_allow_html=True)

    with st.spinner("Syncing market feed..."):
        quotes = fetch_bulk_quotes(yf_syms)

    rows = []
    for s, q in quotes.items():
        ltp, prev = q["ltp"], q["prev"]
        c1d = round((ltp - prev) / prev * 100, 2) if (prev and prev > 0 and ltp) else None
        p1m = st.session_state.prev_px.get(s)
        c1m = round((ltp - p1m) / p1m * 100, 2) if (p1m and p1m > 0 and ltp) else None
        rows.append({"Symbol": s.replace(".NS", ""), "Sector": sec_map.get(s, "Other"), "LTP": round(ltp, 2), "1m %": c1m, "1d %": c1d, "abs1m": abs(c1m) if c1m is not None else -1})

    st.session_state.prev_px = {s: q["ltp"] for s, q in quotes.items()}
    df = pd.DataFrame(rows)

    g_cnt = int((df["1d %"] > 0).sum()) if not df.empty else 0
    l_cnt = int((df["1d %"] < 0).sum()) if not df.empty else 0
    tg = df.loc[df["1d %"].idxmax()] if (not df.empty and not df["1d %"].isna().all()) else None
    tl = df.loc[df["1d %"].idxmin()] if (not df.empty and not df["1d %"].isna().all()) else None
    tg_txt = f"{tg['Symbol']} (+{tg['1d %']:.2f}%)" if tg is not None else "-"
    tl_txt = f"{tl['Symbol']} ({tl['1d %']:.2f}%)" if tl is not None else "-"

    st.markdown(f"""
    <div class="tv-grid">
        <div class="tv-card"><div class="tv-lbl">Adv / Dec</div><div class="tv-val"><span class="tv-g">{g_cnt}</span> / <span class="tv-r">{l_cnt}</span></div></div>
        <div class="tv-card"><div class="tv-lbl">Top Gainer (1D)</div><div class="tv-val tv-g">{tg_txt}</div></div>
        <div class="tv-card"><div class="tv-lbl">Top Loser (1D)</div><div class="tv-val tv-r">{tl_txt}</div></div>
    </div>
    """, unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    q_txt = c1.text_input("Search", placeholder="🔍 Ticker (e.g. RELIANCE)...", label_visibility="collapsed")
    secs = ["All Sectors"] + (sorted(df["Sector"].dropna().unique().tolist()) if not df.empty else [])
    sel_sec = c2.selectbox("Sector", secs, label_visibility="collapsed")
    sort_by = st.radio("Sort", ["🔥 1m Movers", "🚀 1m Gainers", "🔻 1m Losers", "📈 1d Gainers", "📉 1d Losers"], horizontal=True, label_visibility="collapsed")

    if df.empty:
        st.warning("No market data returned yet. Retrying on next cycle...")
        return

    if q_txt:
        df = df[df["Symbol"].str.contains(q_txt.strip().upper(), na=False)]
    if sel_sec != "All Sectors":
        df = df[df["Sector"] == sel_sec]

    sort_map = {
        "🔥 1m Movers": (["abs1m", "1d %"], [False, False]),
        "🚀 1m Gainers": (["1m %"], [False]),
        "🔻 1m Losers": (["1m %"], [True]),
        "📈 1d Gainers": (["1d %"], [False]),
        "📉 1d Losers": (["1d %"], [True]),
    }
    cols, asc = sort_map[sort_by]
    df = df.sort_values(cols, ascending=asc, na_position="last")

    styled = df[["Symbol", "LTP", "1m %", "1d %", "Sector"]].style.map(color_pct, subset=["1m %", "1d %"]).format({"LTP": "₹{:.2f}", "1m %": "{:+.2f}%", "1d %": "{:+.2f}%"}, na_rep="—")
    st.dataframe(styled, height=540, use_container_width=True, hide_index=True)

render_scanner()
