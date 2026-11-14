import json
from datetime import datetime
from zoneinfo import ZoneInfo
import pandas as pd
import streamlit as st
import streamlit.components.v1 as components
import yfinance as yf

st.set_page_config(layout="wide", page_title="Nifty 500 — TradingView Screener", initial_sidebar_state="collapsed")

st.markdown("""
<style>
.stApp { background-color: #131722; color: #D1D4DC; }
.block-container { padding: 3.1rem 0.65rem 0.5rem 0.65rem; max-width: 100%; }
.tv-topbar { display: flex; justify-content: space-between; align-items: center; background: #1E222D; border: 1px solid #2A2E39; border-radius: 6px; padding: 10px 14px; margin-bottom: 10px; }
.tv-brand { display: flex; align-items: center; gap: 8px; }
.tv-logo { background: #2962FF; color: #FFFFFF; font-weight: 800; font-size: 0.85rem; padding: 4px 7px; border-radius: 4px; }
.tv-title { font-size: 1.05rem; font-weight: 700; color: #FFFFFF; line-height: 1.1; }
.tv-sub { font-size: 0.72rem; color: #787B86; margin-top: 2px; }
.tv-live { background: rgba(8,153,129,0.16); color: #089981; border: 1px solid #089981; padding: 4px 9px; border-radius: 4px; font-size: 0.72rem; font-weight: 700; white-space: nowrap; }
.tv-closed { background: rgba(242,54,69,0.16); color: #F23645; border: 1px solid #F23645; padding: 4px 9px; border-radius: 4px; font-size: 0.72rem; font-weight: 700; white-space: nowrap; }
div[role="radiogroup"] { background: #1E222D; border: 1px solid #2A2E39; border-radius: 6px; padding: 4px; gap: 4px; margin-bottom: 6px; width: fit-content; }
div[role="radiogroup"] label { background: transparent !important; border: none !important; border-radius: 4px !important; padding: 5px 14px !important; margin: 0 !important; color: #B2B5BE !important; font-size: 0.82rem !important; font-weight: 600 !important; }
div[role="radiogroup"] label:has(input:checked) { background: #2962FF !important; color: #FFFFFF !important; }
div[role="radiogroup"] label > div:first-child { display: none !important; }
</style>
""", unsafe_allow_html=True)

NIFTY_500_RAW = """
360ONE,ABB,ACC,ACMESOLAR,AIAENG,APLAPOLLO,AUBANK,AWL,AADHARHFC,AARTIIND,AAVAS,ABBOTINDIA,ACE,ACUTAAS,ADANIENSOL,ADANIENT,ADANIGREEN,ADANIPORTS,ADANIPOWER,ATGL,ABCAPITAL,ABREL,ABSLAMC,CPPLUS,AEGISLOG,AEGISVOPAK,AETHER,AFCONS,AFFLE,AJANTPHARM,ALKEM,ABDL,ARE&M,AMBER,AMBUJACEM,ANANDRATHI,ANANTRAJ,ANGELONE,ANTHEM,ANURAS,APARINDS,APOLLOHOSP,APOLLOTYRE,APTUS,ASAHIINDIA,ASHOKLEY,ASIANPAINT,ASTERDM,ASTRAL,ATHERENERG,ATUL,AUROPHARMA,AIIL,AVANTIFEED,DMART,AXISBANK,AZAD,BEML,BLS,BSE,BAGMANE,BAJAJ-AUTO,BAJFINANCE,BAJAJFINSV,BAJAJHLDNG,BAJAJHFL,BALKRISIND,BALRAMCHIN,BANDHANBNK,BANKBARODA,BANKINDIA,MAHABANK,BATAINDIA,BELRISE,BERGEPAINT,BHARATCOAL,BDL,BEL,BHARATFORG,BHEL,BPCL,BHARTIARTL,BHARTIHEXA,GROWW,BIOCON,BSOFT,BBOX,BLUESTARCO,BOSCHLTD,FIRSTCRY,BRIGADE,BRITANNIA,BIRET,CCL,CESC,CGPOWER,CIEINDIA,CRISIL,CANFINHOME,CANBK,CANHLIFE,CAPLIPOINT,CGCL,CARBORUNIV,CARTRADE,CASTROLIND,CEATLTD,CEMPRO,CENTRALBK,CDSL,CMPDI,CHAMBLFERT,CHENNPETRO,CHOICEIN,CHOLAHLDNG,CHOLAFIN,CIPLA,CUB,CLEANMAX,CLEAN,COALINDIA,COCHINSHIP,COFORGE,COHANCE,COLPAL,CAMS,CONCORDBIO,CONCOR,COROMANDEL,CRAFTSMAN,CREDITACC,CROMPTON,CUMMINSIND,CUPID,CYIENT,DLF,DOMS,DABUR,DALBHARAT,DATAPATTNS,DEEPAKFERT,DEEPAKNTR,DELHIVERY,DEVYANI,DIVISLAB,DIXON,LALPATHLAB,DRREDDY,EIDPARRY,EIHOTEL,EMBASSY,EICHERMOT,ELECON,ELGIEQUIP,EMAMILTD,EMCURE,EMMVEE,ENDURANCE,ENGINERSIN,ESCORTS,ETERNAL,EXIDEIND,NYKAA,FEDERALBNK,FACT,FINCABLES,FSL,FIVESTAR,FORCEMOT,FORTIS,FRACTAL,GAIL,GVT&D,GMRAIRPORT,GABRIEL,GALLANTT,GRSE,GICRE,GILLETTE,GLAND,GLAXO,GLENMARK,MEDANTA,GPIL,GODFRYPHLP,GODREJCP,GODREJIND,GODREJPROP,GRANULES,GRAPHITE,GRASIM,GRAVITA,GESHIP,FLUOROCHEM,GMDCLTD,HBLENGINE,HCLTECH,HDBFS,HDFCAMC,HDFCBANK,HDFCLIFE,HEGAM,HFCL,HAVELLS,HEROMOTOCO,HEXT,HSCL,HINDALCO,HAL,HINDCOPPER,HINDPETRO,HINDUNILVR,HINDZINC,POWERINDIA,HOMEFIRST,HONASA,HONAUT,HUDCO,HYUNDAI,ICICIBANK,ICICILIFE,ICICIGI,ICICIAMC,IDBI,IDFCFIRSTB,IFCI,IIFL,INOXINDIA,IRB,IRCON,ITCHOTELS,ITC,ITI,INDIACEM,INDIAMART,INDIANB,IEX,INDHOTEL,IOC,IOB,IRCTC,IRFC,IREDA,IGL,INDUSTOWER,INDUSINDBK,NAUKRI,INFY,INOXWIND,INTELLECT,INDIGO,IGIL,IKS,IPCALAB,JKCEMENT,JBMA,JKTYRE,JMFINANCIL,JSWCEMENT,JSWENERGY,JSWINFRA,JSWSTEEL,JAINREC,JPPOWER,J&KBANK,JINDALSAW,JSL,JINDALSTEL,JIOFIN,JUBLFOOD,JUBLINGREA,JWL,JYOTICNC,KPRMILL,KEI,KPITTECH,KSB,KAJARIACER,KPIL,KALYANKJIL,KARURVYSYA,KAYNES,KEC,KFINTECH,KIRLOSBROS,KIRLOSENG,KOTAKBANK,KIMS,LTF,LTTS,LGEINDIA,LICHSGFIN,LTFOODS,LTM,LT,LAURUSLABS,LEMONTREE,LENSKART,LICI,LINDEINDIA,LLOYDSME,LODHA,LUPIN,MMTC,MRF,MTARTECH,MGL,M&MFIN,M&M,MANAPPURAM,MRPL,MANKIND,MARICO,MARUTI,MFSL,MAXHEALTH,MAZDOCK,MEESHO,MINDACORP,MSUMI,MOTILALOFS,MPHASIS,MCX,MUTHOOTFIN,NATCOPHARM,NBCC,NCC,NHPC,NLCINDIA,NMDC,NSLNISP,NTPCGREEN,NTPC,NH,NATIONALUM,NAVA,NAVINFLUOR,NESTLEIND,NETWEB,NEULANDLAB,NAM-INDIA,NUVAMA,NUVOCO,OBEROIRLTY,ONGC,OIL,OLAELEC,OLECTRA,PAYTM,ONESOURCE,OFSS,POLICYBZR,PCBL,PGEL,PIIND,PNBHOUSING,PTCIL,PVRINOX,PAGEIND,PARADEEP,PATANJALI,PERSISTENT,PETRONET,PHOENIXLTD,PWL,PIDILITIND,PINELABS,PIRAMALFIN,PPLPHARMA,POLYMED,POLYCAB,POONAWALLA,PFC,POWERGRID,PREMIERENE,PRESTIGE,PFOCUS,PRIVISCL,PNB,RRKABEL,RBLBANK,RECLTD,RHIM,RITES,RADICO,RVNL,RAILTEL,RAINBOW,RKFORGE,REDINGTON,RELIANCE,RPOWER,RUBICON,SBICARD,SBILIFE,SJVN,SHRIPISTON,SRF,SAGILITY,SAILIFE,SAMMAANCAP,MOTHERSON,SANSERA,SARDAEN,SCHAEFFLER,SCHNEIDER,SCI,SHREECEM,SHRIRAMFIN,SHYAMMETL,ENRIN,SIEMENS,SIGNATURE,SOBHA,SOLARINDS,SONACOMS,STARHEALTH,SBIN,SAIL,STLTECH,SUMICHEM,SUNPHARMA,SUNTV,SUNDARMFIN,SUPREMEIND,SUZLON,SWANCORP,SWIGGY,SYNGENE,SYRMA,TBOTEK,TDPOWERSYS,TVSMOTOR,TATACAP,TATACHEM,TATACOMM,TCS,TATACONSUM,TATAELXSI,TATAINVEST,TMCV,TMPV,TATAPOWER,TATASTEEL,TATATECH,TTML,TECHM,TECHNOE,TEGA,TEJASNET,TENNIND,THANGAMAYL,NIACL,RAMCOCEM,THERMAX,TIMKEN,TITAGARH,TITAN,TORNTPHARM,TORNTPOWER,TARIL,TRENT,TRIDENT,TRITURBINE,TIINDIA,UCOBANK,UNOMINDA,UPL,UTIAMC,ULTRACEMCO,UNIONBANK,UBL,UNITDSPR,URBANCO,USHAMART,VTL,VBL,VAML,VISL,VEDL,VOGL,VEDPOWER,VIJAYA,VMM,IDEA,VOLTAS,WAAREEENER,WELCORP,WELSPUNLIV,WHIRLPOOL,WIPRO,WOCKPHARMA,YESBANK,ZFCVINDIA,ZEEL,ZENTEC,ZENSARTECH,ZYDUSLIFE,ZYDUSWELL,ECLERX
"""

YF_SYMS = [s.strip() + ".NS" for s in NIFTY_500_RAW.replace("\n", "").split(",") if s.strip()]

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
<style>
* { box-sizing: border-box; margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, "Trebuchet MS", Roboto, sans-serif; }
body { background: #131722; color: #D1D4DC; }
.wrap { height: 73vh; overflow-y: auto; border: 1px solid #2A2E39; border-radius: 6px; background: #131722; }
table { width: 100%; border-collapse: collapse; font-size: 13.5px; }
thead th { position: sticky; top: 0; background: #1E222D; color: #787B86; font-weight: 700; text-align: right; padding: 10px; border-bottom: 1px solid #2A2E39; font-size: 12px; text-transform: uppercase; cursor: pointer; user-select: none; z-index: 2; }
thead th:hover { color: #FFFFFF; background: #262B38; }
thead th:first-child { text-align: left; }
tbody td { padding: 9px 10px; border-bottom: 1px solid #1E222D; text-align: right; color: #D1D4DC; }
tbody td:first-child { text-align: left; font-weight: 700; color: #FFFFFF; }
tbody tr:hover { background: #1E222D; }
.pos { color: #089981 !important; font-weight: 600; background: rgba(8,153,129,0.10); }
.neg { color: #F23645 !important; font-weight: 600; background: rgba(242,54,69,0.10); }
.neu { color: #787B86 !important; }
.arr { font-size: 10px; margin-left: 3px; color: #2962FF; }
</style>
</head>
<body>
<div class="wrap">
<table>
<thead>
<tr>
<th onclick="sortBy('sym', false)">Symbol <span class="arr" id="a-sym"></span></th>
<th onclick="sortBy('ltp', true)">LTP <span class="arr" id="a-ltp"></span></th>
<th onclick="sortBy('m1', true)">1m % <span class="arr" id="a-m1"></span></th>
<th onclick="sortBy('d1', true)">1d % <span class="arr" id="a-d1">▼</span></th>
</tr>
</thead>
<tbody id="tb"></tbody>
</table>
</div>
<script>
const DATA = __DATA_JSON__;
let dir = { sym: true, ltp: false, m1: false, d1: false };
function fmtCell(v) {
    if (v === null || v === undefined) return '<td class="neu">—</td>';
    if (v > 0) return '<td class="pos">+' + v.toFixed(2) + '%</td>';
    if (v < 0) return '<td class="neg">' + v.toFixed(2) + '%</td>';
    return '<td class="neu">0.00%</td>';
}
function render(rows) {
    const tb = document.getElementById("tb");
    tb.innerHTML = rows.map(r =>
        '<tr><td>' + r.sym + '</td><td>₹' + r.ltp.toLocaleString('en-IN', {minimumFractionDigits:2, maximumFractionDigits:2}) + '</td>' + fmtCell(r.m1) + fmtCell(r.d1) + '</tr>'
    ).join('');
}
function sortBy(key, isNum) {
    dir[key] = !dir[key];
    const asc = dir[key];
    document.querySelectorAll('.arr').forEach(e => e.textContent = '');
    document.getElementById('a-' + key).textContent = asc ? '▲' : '▼';
    const sorted = [...DATA].sort((a, b) => {
        if (!isNum) return asc ? a.sym.localeCompare(b.sym) : b.sym.localeCompare(a.sym);
        const va = (a[key] === null || a[key] === undefined) ? -999999 : a[key];
        const vb = (b[key] === null || b[key] === undefined) ? -999999 : b[key];
        return asc ? va - vb : vb - va;
    });
    render(sorted);
}
render(DATA);
</script>
</body>
</html>
"""

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

@st.fragment(run_every=60)
def render_scanner():
    prev_px = st.session_state.setdefault("prev_px", {})
    now = datetime.now(ZoneInfo("Asia/Kolkata"))
    is_open = (now.weekday() < 5) and (555 <= now.hour * 60 + now.minute <= 930)
