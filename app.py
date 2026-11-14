from datetime import datetime
from zoneinfo import ZoneInfo
import pandas as pd
import streamlit as st
import yfinance as yf

st.set_page_config(layout="wide", page_title="Nifty 500 — 1m Candle Screener", initial_sidebar_state="collapsed")

st.markdown("""
<style>
div[data-testid="stStatusWidget"] { display: none !important; }
.block-container { padding: 3.1rem 0.65rem 1rem 0.65rem; max-width: 100%; }
.tv-topbar { display: flex; justify-content: space-between; align-items: center; background: #1E222D; border: 1px solid #2A2E39; border-radius: 6px; padding: 10px 14px; margin-bottom: 10px; }
.tv-brand { display: flex; align-items: center; gap: 8px; }
.tv-logo { background: #2962FF; color: #FFFFFF; font-weight: 800; font-size: 0.85rem; padding: 4px 7px; border-radius: 4px; letter-spacing: 0.5px; }
.tv-title { font-size: 1.05rem; font-weight: 700; color: #FFFFFF; line-height: 1.1; }
.tv-sub { font-size: 0.74rem; color: #B2B5BE; margin-top: 3px; }
.tv-cd { color: #2962FF; font-weight: 700; }
.tv-live { background: rgba(8,153,129,0.16); color: #089981; border: 1px solid #089981; padding: 4px 9px; border-radius: 4px; font-size: 0.72rem; font-weight: 700; white-space: nowrap; }
.tv-closed { background: rgba(242,54,69,0.16); color: #F23645; border: 1px solid #F23645; padding: 4px 9px; border-radius: 4px; font-size: 0.72rem; font-weight: 700; white-space: nowrap; }
div[role="radiogroup"] { background: #1E222D; border: 1px solid #2A2E39; border-radius: 6px; padding: 4px; gap: 4px; margin-bottom: 8px; width: fit-content; }
div[role="radiogroup"] label { background: transparent !important; border: none !important; border-radius: 4px !important; padding: 5px 14px !important; margin: 0 !important; color: #B2B5BE !important; font-size: 0.82rem !important; font-weight: 600 !important; }
div[role="radiogroup"] label:has(input:checked) { background: #2962FF !important; color: #FFFFFF !important; }
div[role="radiogroup"] label > div:first-child { display: none !important; }
[data-testid="stDataFrame"] { border: 1px solid #2A2E39 !important; border-radius: 6px !important; }
[data-testid="stDataFrame"] [role="columnheader"] { background-color: #242938 !important; color: #FFFFFF !important; font-size: 15px !important; font-weight: 800 !important; justify-content: center !important; text-align: center !important; }
[data-testid="stDataFrame"] [role="columnheader"] * { justify-content: center !important; text-align: center !important; font-size: 15px !important; font-weight: 800 !important; color: #FFFFFF !important; }
[data-testid="stDataFrame"] [role="gridcell"] { justify-content: center !important; text-align: center !important; }
</style>
""", unsafe_allow_html=True)

NIFTY_500_RAW = """
360ONE,ABB,ACC,ACMESOLAR,AIAENG,APLAPOLLO,AUBANK,AWL,AADHARHFC,AARTIIND,AAVAS,ABBOTINDIA,ACE,ACUTAAS,ADANIENSOL,ADANIENT,ADANIGREEN,ADANIPORTS,ADANIPOWER,ATGL,ABCAPITAL,ABREL,ABSLAMC,CPPLUS,AEGISLOG,AEGISVOPAK,AETHER,AFCONS,AFFLE,AJANTPHARM,ALKEM,ABDL,ARE&M,AMBER,AMBUJACEM,ANANDRATHI,ANANTRAJ,ANGELONE,ANTHEM,ANURAS,APARINDS,APOLLOHOSP,APOLLOTYRE,APTUS,ASAHIINDIA,ASHOKLEY,ASIANPAINT,ASTERDM,ASTRAL,ATHERENERG,ATUL,AUROPHARMA,AIIL,AVANTIFEED,DMART,AXISBANK,AZAD,BEML,BLS,BSE,BAGMANE,BAJAJ-AUTO,BAJFINANCE,BAJAJFINSV,BAJAJHLDNG,BAJAJHFL,BALKRISIND,BALRAMCHIN,BANDHANBNK,BANKBARODA,BANKINDIA,MAHABANK,BATAINDIA,BELRISE,BERGEPAINT,BHARATCOAL,BDL,BEL,BHARATFORG,BHEL,BPCL,BHARTIARTL,BHARTIHEXA,GROWW,BIOCON,BSOFT,BBOX,BLUESTARCO,BOSCHLTD,FIRSTCRY,BRIGADE,BRITANNIA,BIRET,CCL,CESC,CGPOWER,CIEINDIA,CRISIL,CANFINHOME,CANBK,CANHLIFE,CAPLIPOINT,CGCL,CARBORUNIV,CARTRADE,CASTROLIND,CEATLTD,CEMPRO,CENTRALBK,CDSL,CMPDI,CHAMBLFERT,CHENNPETRO,CHOICEIN,CHOLAHLDNG,CHOLAFIN,CIPLA,CUB,CLEANMAX,CLEAN,COALINDIA,COCHINSHIP,COFORGE,COHANCE,COLPAL,CAMS,CONCORDBIO,CONCOR,COROMANDEL,CRAFTSMAN,CREDITACC,CROMPTON,CUMMINSIND,CUPID,CYIENT,DLF,DOMS,DABUR,DALBHARAT,DATAPATTNS,DEEPAKFERT,DEEPAKNTR,DELHIVERY,DEVYANI,DIVISLAB,DIXON,LALPATHLAB,DRREDDY,EIDPARRY,EIHOTEL,EMBASSY,EICHERMOT,ELECON,ELGIEQUIP,EMAMILTD,EMCURE,EMMVEE,ENDURANCE,ENGINERSIN,ESCORTS,ETERNAL,EXIDEIND,NYKAA,FEDERALBNK,FACT,FINCABLES,FSL,FIVESTAR,FORCEMOT,FORTIS,FRACTAL,GAIL,GVT&D,GMRAIRPORT,GABRIEL,GALLANTT,GRSE,GICRE,GILLETTE,GLAND,GLAXO,GLENMARK,MEDANTA,GPIL,GODFRYPHLP,GODREJCP,GODREJIND,GODREJPROP,GRANULES,GRAPHITE,GRASIM,GRAVITA,GESHIP,FLUOROCHEM,GMDCLTD,HBLENGINE,HCLTECH,HDBFS,HDFCAMC,HDFCBANK,HDFCLIFE,HEGAM,HFCL,HAVELLS,HEROMOTOCO,HEXT,HSCL,HINDALCO,HAL,HINDCOPPER,HINDPETRO,HINDUNILVR,HINDZINC,POWERINDIA,HOMEFIRST,HONASA,HONAUT,HUDCO,HYUNDAI,ICICIBANK,ICICILIFE,ICICIGI,ICICIAMC,IDBI,IDFCFIRSTB,IFCI,IIFL,INOXINDIA,IRB,IRCON,ITCHOTELS,ITC,ITI,INDIACEM,INDIAMART,INDIANB,IEX,INDHOTEL,IOC,IOB,IRCTC,IRFC,IREDA,IGL,INDUSTOWER,INDUSINDBK,NAUKRI,INFY,INOXWIND,INTELLECT,INDIGO,IGIL,IKS,IPCALAB,JKCEMENT,JBMA,JKTYRE,JMFINANCIL,JSWCEMENT,JSWENERGY,JSWINFRA,JSWSTEEL,JAINREC,JPPOWER,J&KBANK,JINDALSAW,JSL,JINDALSTEL,JIOFIN,JUBLFOOD,JUBLINGREA,JWL,JYOTICNC,KPRMILL,KEI,KPITTECH,KSB,KAJARIACER,KPIL,KALYANKJIL,KARURVYSYA,KAYNES,KEC,KFINTECH,KIRLOSBROS,KIRLOSENG,KOTAKBANK,KIMS,LTF,LTTS,LGEINDIA,LICHSGFIN,LTFOODS,LTM,LT,LAURUSLABS,LEMONTREE,LENSKART,LICI,LINDEINDIA,LLOYDSME,LODHA,LUPIN,MMTC,MRF,MTARTECH,MGL,M&MFIN,M&M,MANAPPURAM,MRPL,MANKIND,MARICO,MARUTI,MFSL,MAXHEALTH,MAZDOCK,MEESHO,MINDACORP,MSUMI,MOTILALOFS,MPHASIS,MCX,MUTHOOTFIN,NATCOPHARM,NBCC,NCC,NHPC,NLCINDIA,NMDC,NSLNISP,NTPCGREEN,NTPC,NH,NATIONALUM,NAVA,NAVINFLUOR,NESTLEIND,NETWEB,NEULANDLAB,NAM-INDIA,NUVAMA,NUVOCO,OBEROIRLTY,ONGC,OIL,OLAELEC,OLECTRA,PAYTM,ONESOURCE,OFSS,POLICYBZR,PCBL,PGEL,PIIND,PNBHOUSING,PTCIL,PVRINOX,PAGEIND,PARADEEP,PATANJALI,PERSISTENT,PETRONET,PHOENIXLTD,PWL,PIDILITIND,PINELABS,PIRAMALFIN,PPLPHARMA,POLYMED,POLYCAB,POONAWALLA,PFC,POWERGRID,PREMIERENE,PRESTIGE,PFOCUS,PRIVISCL,PNB,RRKABEL,RBLBANK,RECLTD,RHIM,RITES,RADICO,RVNL,RAILTEL,RAINBOW,RKFORGE,REDINGTON,RELIANCE,RPOWER,RUBICON,SBICARD,SBILIFE,SJVN,SHRIPISTON,SRF,SAGILITY,SAILIFE,SAMMAANCAP,MOTHERSON,SANSERA,SARDAEN,SCHAEFFLER,SCHNEIDER,SCI,SHREECEM,SHRIRAMFIN,SHYAMMETL,ENRIN,SIEMENS,SIGNATURE,SOBHA,SOLARINDS,SONACOMS,STARHEALTH,SBIN,SAIL,STLTECH,SUMICHEM,SUNPHARMA,SUNTV,SUNDARMFIN,SUPREMEIND,SUZLON,SWANCORP,SWIGGY,SYNGENE,SYRMA,TBOTEK,TDPOWERSYS,TVSMOTOR,TATACAP,TATACHEM,TATACOMM,TCS,TATACONSUM,TATAELXSI,TATAINVEST,TMCV,TMPV,TATAPOWER,TATASTEEL,TATATECH,TTML,TECHM,TECHNOE,TEGA,TEJASNET,TENNIND,THANGAMAYL,NIACL,RAMCOCEM,THERMAX,TIMKEN,TITAGARH,TITAN,TORNTPHARM,TORNTPOWER,TARIL,TRENT,TRIDENT,TRITURBINE,TIINDIA,UCOBANK,UNOMINDA,UPL,UTIAMC,ULTRACEMCO,UNIONBANK,UBL,UNITDSPR,URBANCO,USHAMART,VTL,VBL,VAML,VISL,VEDL,VOGL,VEDPOWER,VIJAYA,VMM,IDEA,VOLTAS,WAAREEENER,WELCORP,WELSPUNLIV,WHIRLPOOL,WIPRO,WOCKPHARMA,YESBANK,ZFCVINDIA,ZEEL,ZENTEC,ZENSARTECH,ZYDUSLIFE,ZYDUSWELL,ECLERX
"""

YF_SYMS = [s.strip() + ".NS" for s in NIFTY_500_RAW.replace("\n", "").split(",") if s.strip()]

@st.cache_data(ttl=55, show_spinner=False)
def fetch_1m_candles(syms):
    # Fetch last 2 days of 1-minute candles in bulk
    raw = yf.download(tickers=syms, period="2d", interval="1m", group_by="ticker", threads=True, progress=False)
    quotes = {}
    latest_ts = None
    ist = ZoneInfo("Asia/Kolkata")

    for s in syms:
        try:
            c = raw[s]["Close"].dropna()
            if c.empty: continue
            c_ist = c.tz_convert(ist) if c.index.tz is not None else c.tz_localize("UTC").tz_convert(ist)

            last_dt = c_ist.index[-1]
            if latest_ts is None or last_dt > latest_ts: latest_ts = last_dt

            last_close = float(c_ist.iloc[-1])
            prev_1m_close = float(c_ist.iloc[-2]) if len(c_ist) >= 2 else None

            # Previous trading day's final candle close for 1d %
            prev_day_bars = c_ist[c_ist.index.date < last_dt.date()]
            prev_day_close = float(prev_day_bars.iloc[-1]) if not prev_day_bars.empty else None

            quotes[s] = {
                "ltp": last_close,
                "prev_1m": prev_1m_close,
                "prev_day": prev_day_close,
                "candle_time": last_dt.strftime("%I:%M %p"),
            }
        except Exception:
            pass
    return quotes, latest_ts

def color_pct(val):
    if pd.isna(val) or val == 0: return "color: #787B86;"
    if val > 0: return "color: #089981; font-weight: 700;"
    return "color: #F23645; font-weight: 700;"

@st.fragment(run_every=60)
def render_scanner():
    now_ist = datetime.now(ZoneInfo("Asia/Kolkata"))
    is_open = (now_ist.weekday() < 5) and (555 <= now_ist.hour * 60 + now_ist.minute <= 930)
    badge = '<span class="tv-live">● NSE LIVE</span>' if is_open else '<span class="tv-closed">● MARKET CLOSED</span>'

    quotes, latest_ts = fetch_1m_candles(YF_SYMS)

    if latest_ts is not None:
        candle_str = latest_ts.strftime("%d %b · %I:%M %p IST")
        next_candle_str = (latest_ts + pd.Timedelta(minutes=1)).strftime("%I:%M %p")
    else:
        candle_str = "Syncing..."
        next_candle_str = "—"

    st.markdown(f'<div class="tv-topbar"><div class="tv-brand"><div class="tv-logo">TV</div><div><div class="tv-title">NIFTY 500 · 1M CANDLE SCREENER</div><div class="tv-sub">Stocks: {len(quotes)}/{len(YF_SYMS)} · Last Candle: <span class="tv-cd">{candle_str}</span> · Next Bar: {next_candle_str}</div></div></div>{badge}</div>', unsafe_allow_html=True)

    rows = []
    for s, q in quotes.items():
        ltp = q["ltp"]
        p1m = q["prev_1m"]
        p1d = q["prev_day"]
        c1m = round((ltp - p1m) / p1m * 100, 2) if (p1m and p1m > 0 and ltp) else None
        c1d = round((ltp - p1d) / p1d * 100, 2) if (p1d and p1d > 0 and ltp) else None
        rows.append({"Symbol": s.replace(".NS", ""), "Last Close": round(ltp, 2), "Candle": q["candle_time"], "1m %": c1m, "1d %": c1d})

    df = pd.DataFrame(rows)

    flt = st.radio("Filter", ["All", "1m Gainers", "1m Losers"], horizontal=True, label_visibility="collapsed")

    if df.empty:
        st.warning("No 1-minute candle data returned yet. Retrying on next cycle...")
