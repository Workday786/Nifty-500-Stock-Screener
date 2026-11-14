from datetime import datetime
from zoneinfo import ZoneInfo
import pandas as pd
import streamlit as st
import yfinance as yf

st.set_page_config(layout="wide", page_title="Nifty 500 — TradingView Screener", initial_sidebar_state="collapsed")

st.markdown("""
<style>
.stApp { background-color: #131722; color: #D1D4DC; }
.block-container { padding: 3.1rem 0.65rem 1rem 0.65rem; max-width: 100%; }
.tv-topbar { display: flex; justify-content: space-between; align-items: center; background: #1E222D; border: 1px solid #2A2E39; border-radius: 6px; padding: 10px 14px; margin-bottom: 10px; }
.tv-brand { display: flex; align-items: center; gap: 8px; }
.tv-logo { background: #2962FF; color: #FFFFFF; font-weight: 800; font-size: 0.85rem; padding: 4px 7px; border-radius: 4px; }
.tv-title { font-size: 1.05rem; font-weight: 700; color: #FFFFFF; line-height: 1.1; }
.tv-sub { font-size: 0.72rem; color: #787B86; margin-top: 2px; }
.tv-live { background: rgba(8,153,129,0.16); color: #089981; border: 1px solid #089981; padding: 4px 9px; border-radius: 4px; font-size: 0.72rem; font-weight: 700; white-space: nowrap; }
.tv-closed { background: rgba(242,54,69,0.16); color: #F23645; border: 1px solid #F23645; padding: 4px 9px; border-radius: 4px; font-size: 0.72rem; font-weight: 700; white-space: nowrap; }
.tv-table-wrap { max-height: 74vh; overflow-y: auto; border: 1px solid #2A2E39; border-radius: 6px; background: #131722; }
.tv-tbl { width: 100%; border-collapse: collapse; font-size: 0.86rem; }
.tv-tbl thead th { position: sticky; top: 0; background: #1E222D; color: #787B86; font-weight: 600; text-align: right; padding: 9px 10px; border-bottom: 1px solid #2A2E39; font-size: 0.76rem; text-transform: uppercase; }
.tv-tbl thead th:first-child { text-align: left; }
.tv-tbl tbody td { padding: 8px 10px; border-bottom: 1px solid #1E222D; text-align: right; color: #D1D4DC; }
.tv-tbl tbody td:first-child { text-align: left; font-weight: 700; color: #FFFFFF; }
.tv-tbl tbody tr:hover { background: #1E222D; }
.tv-pos { color: #089981 !important; font-weight: 600; background: rgba(8,153,129,0.10); }
.tv-neg { color: #F23645 !important; font-weight: 600; background: rgba(242,54,69,0.10); }
.tv-neu { color: #787B86 !important; }
</style>
""", unsafe_allow_html=True)

NIFTY_500_RAW = """
360ONE,ABB,ACC,ACMESOLAR,AIAENG,APLAPOLLO,AUBANK,AWL,AADHARHFC,AARTIIND,AAVAS,ABBOTINDIA,ACE,ACUTAAS,ADANIENSOL,ADANIENT,ADANIGREEN,ADANIPORTS,ADANIPOWER,ATGL,ABCAPITAL,ABREL,ABSLAMC,CPPLUS,AEGISLOG,AEGISVOPAK,AETHER,AFCONS,AFFLE,AJANTPHARM,ALKEM,ABDL,ARE&M,AMBER,AMBUJACEM,ANANDRATHI,ANANTRAJ,ANGELONE,ANTHEM,ANURAS,APARINDS,APOLLOHOSP,APOLLOTYRE,APTUS,ASAHIINDIA,ASHOKLEY,ASIANPAINT,ASTERDM,ASTRAL,ATHERENERG,ATUL,AUROPHARMA,AIIL,AVANTIFEED,DMART,AXISBANK,AZAD,BEML,BLS,BSE,BAGMANE,BAJAJ-AUTO,BAJFINANCE,BAJAJFINSV,BAJAJHLDNG,BAJAJHFL,BALKRISIND,BALRAMCHIN,BANDHANBNK,BANKBARODA,BANKINDIA,MAHABANK,BATAINDIA,BELRISE,BERGEPAINT,BHARATCOAL,BDL,BEL,BHARATFORG,BHEL,BPCL,BHARTIARTL,BHARTIHEXA,GROWW,BIOCON,BSOFT,BBOX,BLUESTARCO,BOSCHLTD,FIRSTCRY,BRIGADE,BRITANNIA,BIRET,CCL,CESC,CGPOWER,CIEINDIA,CRISIL,CANFINHOME,CANBK,CANHLIFE,CAPLIPOINT,CGCL,CARBORUNIV,CARTRADE,CASTROLIND,CEATLTD,CEMPRO,CENTRALBK,CDSL,CMPDI,CHAMBLFERT,CHENNPETRO,CHOICEIN,CHOLAHLDNG,CHOLAFIN,CIPLA,CUB,CLEANMAX,CLEAN,COALINDIA,COCHINSHIP,COFORGE,COHANCE,COLPAL,CAMS,CONCORDBIO,CONCOR,COROMANDEL,CRAFTSMAN,CREDITACC,CROMPTON,CUMMINSIND,CUPID,CYIENT,DLF,DOMS,DABUR,DALBHARAT,DATAPATTNS,DEEPAKFERT,DEEPAKNTR,DELHIVERY,DEVYANI,DIVISLAB,DIXON,LALPATHLAB,DRREDDY,EIDPARRY,EIHOTEL,EMBASSY,EICHERMOT,ELECON,ELGIEQUIP,EMAMILTD,EMCURE,EMMVEE,ENDURANCE,ENGINERSIN,ESCORTS,ETERNAL,EXIDEIND,NYKAA,FEDERALBNK,FACT,FINCABLES,FSL,FIVESTAR,FORCEMOT,FORTIS,FRACTAL,GAIL,GVT&D,GMRAIRPORT,GABRIEL,GALLANTT,GRSE,GICRE,GILLETTE,GLAND,GLAXO,GLENMARK,MEDANTA,GPIL,GODFRYPHLP,GODREJCP,GODREJIND,GODREJPROP,GRANULES,GRAPHITE,GRASIM,GRAVITA,GESHIP,FLUOROCHEM,GMDCLTD,HBLENGINE,HCLTECH,HDBFS,HDFCAMC,HDFCBANK,HDFCLIFE,HEGAM,HFCL,HAVELLS,HEROMOTOCO,HEXT,HSCL,HINDALCO,HAL,HINDCOPPER,HINDPETRO,HINDUNILVR,HINDZINC,POWERINDIA,HOMEFIRST,HONASA,HONAUT,HUDCO,HYUNDAI,ICICIBANK,ICICILIFE,ICICIGI,ICICIAMC,IDBI,IDFCFIRSTB,IFCI,IIFL,INOXINDIA,IRB,IRCON,ITCHOTELS,ITC,ITI,INDIACEM,INDIAMART,INDIANB,IEX,INDHOTEL,IOC,IOB,IRCTC,IRFC,IREDA,IGL,INDUSTOWER,INDUSINDBK,NAUKRI,INFY,INOXWIND,INTELLECT,INDIGO,IGIL,IKS,IPCALAB,JKCEMENT,JBMA,JKTYRE,JMFINANCIL,JSWCEMENT,JSWENERGY,JSWINFRA,JSWSTEEL,JAINREC,JPPOWER,J&KBANK,JINDALSAW,JSL,JINDALSTEL,JIOFIN,JUBLFOOD,JUBLINGREA,JWL,JYOTICNC,KPRMILL,KEI,KPITTECH,KSB,KAJARIACER,KPIL,KALYANKJIL,KARURVYSYA,KAYNES,KEC,KFINTECH,KIRLOSBROS,KIRLOSENG,KOTAKBANK,KIMS,LTF,LTTS,LGEINDIA,LICHSGFIN,LTFOODS,LTM,LT,LAURUSLABS,LEMONTREE,LENSKART,LICI,LINDEINDIA,LLOYDSME,LODHA,LUPIN,MMTC,MRF,MTARTECH,MGL,M&MFIN,M&M,MANAPPURAM,MRPL,MANKIND,MARICO,MARUTI,MFSL,MAXHEALTH,MAZDOCK,MEESHO,MINDACORP,MSUMI,MOTILALOFS,MPHASIS,MCX,MUTHOOTFIN,NATCOPHARM,NBCC,NCC,NHPC,NLCINDIA,NMDC,NSLNISP,NTPCGREEN,NTPC,NH,NATIONALUM,NAVA,NAVINFLUOR,NESTLEIND,NETWEB,NEULANDLAB,NAM-INDIA,NUVAMA,NUVOCO,OBEROIRLTY,ONGC,OIL,OLAELEC,OLECTRA,PAYTM,ONESOURCE,OFSS,POLICYBZR,PCBL,PGEL,PIIND,PNBHOUSING,PTCIL,PVRINOX,PAGEIND,PARADEEP,PATANJALI,PERSISTENT,PETRONET,PHOENIXLTD,PWL,PIDILITIND,PINELABS,PIRAMALFIN,PPLPHARMA,POLYMED,POLYCAB,POONAWALLA,PFC,POWERGRID,PREMIERENE,PRESTIGE,PFOCUS,PRIVISCL,PNB,RRKABEL,RBLBANK,RECLTD,RHIM,RITES,RADICO,RVNL,RAILTEL,RAINBOW,RKFORGE,REDINGTON,RELIANCE,RPOWER,RUBICON,SBICARD,SBILIFE,SJVN,SHRIPISTON,SRF,SAGILITY,SAILIFE,SAMMAANCAP,MOTHERSON,SANSERA,SARDAEN,SCHAEFFLER,SCHNEIDER,SCI,SHREECEM,SHRIRAMFIN,SHYAMMETL,ENRIN,SIEMENS,SIGNATURE,SOBHA,SOLARINDS,SONACOMS,STARHEALTH,SBIN,SAIL,STLTECH,SUMICHEM,SUNPHARMA,SUNTV,SUNDARMFIN,SUPREMEIND,SUZLON,SWANCORP,SWIGGY,SYNGENE,SYRMA,TBOTEK,TDPOWERSYS,TVSMOTOR,TATACAP,TATACHEM,TATACOMM,TCS,TATACONSUM,TATAELXSI,TATAINVEST,TMCV,TMPV,TATAPOWER,TATASTEEL,TATATECH,TTML,TECHM,TECHNOE,TEGA,TEJASNET,TENNIND,THANGAMAYL,NIACL,RAMCOCEM,THERMAX,TIMKEN,TITAGARH,TITAN,TORNTPHARM,TORNTPOWER,TARIL,TRENT,TRIDENT,TRITURBINE,TIINDIA,UCOBANK,UNOMINDA,UPL,UTIAMC,ULTRACEMCO,UNIONBANK,UBL,UNITDSPR,URBANCO,USHAMART,VTL,VBL,VAML,VISL,VEDL,VOGL,VEDPOWER,VIJAYA,VMM,IDEA,VOLTAS,WAAREEENER,WELCORP,WELSPUNLIV,WHIRLPOOL,WIPRO,WOCKPHARMA,YESBANK,ZFCVINDIA,ZEEL,ZENTEC,ZENSARTECH,ZYDUSLIFE,ZYDUSWELL,ECLERX
"""

YF_SYMS = [s.strip() + ".NS" for s in NIFTY_500_RAW.replace("\n", "").split(",") if s.strip()]

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

if "prev_px" not in st.session_state:
    st.session_state.prev_px = {}

def fmt_cell(val):
    if pd.isna(val):
        return '<td class="tv-neu">—</td>'
    if val > 0:
        return f'<td class="tv-pos">+{val:.2f}%</td>'
    if val < 0:
        return f'<td class="tv-neg">{val:.2f}%</td>'
    return '<td class="tv-neu">0.00%</td>'

@st.fragment(run_every=60)
def render_scanner():
    now = datetime.now(ZoneInfo("Asia/Kolkata"))
    is_open = (now.weekday() < 5) and (555 <= now.hour * 60 + now.minute <= 930)
    badge = '<span class="tv-live">● NSE LIVE</span>' if is_open else '<span class="tv-closed">● MARKET CLOSED</span>'

    with st.spinner("Syncing market feed..."):
        quotes = fetch_bulk_quotes(YF_SYMS)

    st.markdown(f"""
    <div class="tv-topbar">
        <div class="tv-brand">
            <div class="tv-logo">TV</div>
            <div>
                <div class="tv-title">NIFTY 500 SCREENER</div>
                <div class="tv-sub">NSE Cash · {len(quotes)}/{len(YF_SYMS)} Stocks · {now.strftime("%H:%M:%S IST")}</div>
            </div>
        </div>
        {badge}
    </div>
    """, unsafe_allow_html=True)

    rows = []
    for s, q in quotes.items():
        ltp, prev = q["ltp"], q["prev"]
        c1d = round((ltp - prev) / prev * 100, 2) if (prev and prev > 0 and ltp) else None
        p1m = st.session_state.prev_px.get(s)
        c1m = round((ltp - p1m) / p1m * 100, 2) if (p1m and p1m > 0 and ltp) else None
        rows.append({"Symbol": s.replace(".NS", ""), "LTP": round(ltp, 2), "1m %": c1m, "1d %": c1d})

    st.session_state.prev_px = {s: q["ltp"] for s, q in quotes.items()}
    df = pd.DataFrame(rows)

    sort_by = st.radio("Filter", ["All", "1m Gainers", "1m Losers"], horizontal=True, label_visibility="collapsed")

    if df.empty:
        st.warning("No market data returned yet. Retrying on next cycle...")
        return

    if sort_by == "1m Gainers":
        df = df[df["1m %"].notna() & (df["1m %"] > 0)].sort_values("1m %", ascending=False)
    elif sort_by == "1m Losers":
        df = df[df["1m %"].notna() & (df["1m %"] < 0)].sort_values("1m %", ascending=True)
    else:
        df = df.sort_values("1d %", ascending=False, na_position="last")

    if df.empty:
        st.info("No stocks matched this 1-minute filter yet (market may be closed or waiting for next 60s tick).")
        return

    html_rows = []
    for _, r in df.iterrows():
        html_rows.append(
            f"<tr><td>{r['Symbol']}</td><td>₹{r['LTP']:,.2f}</td>{fmt_cell(r['1m %'])}{fmt_cell(r['1d %'])}</tr>"
        )

    table_html = f"""
    <div class="tv-table-wrap">
        <table class="tv-tbl">
            <thead>
                <tr><th>Symbol</th><th>LTP</th><th>1m %</th><th>1d %</th></tr>
            </thead>
            <tbody>{"".join(html_rows)}</tbody>
        </table>
    </div>
    """
    st.markdown(table_html, unsafe_allow_html=True)

render_scanner()
