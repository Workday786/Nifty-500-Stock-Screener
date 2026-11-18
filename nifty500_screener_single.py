"""
NIFTY 500 ONE-MINUTE RESEARCH SCREENER - SINGLE FILE

Install (Windows): py -m pip install "streamlit>=1.37,<2" "yfinance>=0.2.50,<1" "pandas>=2,<4" tzdata
Start: py -m streamlit run nifty500_screener_single.py
Mac: replace 'py' with 'python3'.

Personal research only. Yahoo 1-minute bars may be stale, missing or incomplete;
Yahoo says data is informational and not intended for trading. No broker orders.
The time shown is the START of the completed 1-minute candle, in India time.
"""
from datetime import time as dt_time
from zoneinfo import ZoneInfo
from threading import Thread, Lock
import html
import json
import math
import time

import pandas as pd
import streamlit as st
import streamlit.components.v1 as components
import yfinance as yf

# ---- SIMPLE SETTINGS ----
SCREENER_NAME = "NIFTY 500 · 1-MINUTE SCREENER"  # Change the title here.
TITLE_COLOUR = "#F3B65A"                         # Title colour (warm amber).
REFRESH_SECONDS = 60                             # Time between download attempts.
BATCH_SIZE = 250                                 # Yahoo symbols per batch.
DOWNLOAD_TIMEOUT = 15                            # Request timeout, not a refresh guarantee.
IST = ZoneInfo("Asia/Kolkata")

# Cash-equity constituent snapshot from the official index list. Update when it changes.
# Excludes placeholder DUMMY* and REIT/RR series. EQ and BE series included.
SYMBOLS = '''360ONE, AADHARHFC, AARTIIND, AAVAS, ABB, ABBOTINDIA, ABCAPITAL, ABDL, ABREL, ABSLAMC, ACC, ACE, ACMESOLAR, ACUTAAS, ADANIENSOL, ADANIENT, ADANIGREEN, ADANIPORTS, ADANIPOWER, AEGISLOG, AEGISVOPAK, AETHER, AFCONS, AFFLE, AIAENG, AIIL, AJANTPHARM, ALKEM, AMBER, AMBUJACEM, ANANDRATHI, ANANTRAJ, ANGELONE, ANTHEM, ANURAS, APARINDS, APLAPOLLO, APOLLOHOSP, APOLLOTYRE, APTUS, ARE&M, ASAHIINDIA, ASHOKLEY, ASIANPAINT, ASTERDM, ASTRAL, ATGL, ATHERENERG, ATUL, AUBANK, AUROPHARMA, AVANTIFEED, AWL, AXISBANK, AZAD, BAJAJ-AUTO, BAJAJFINSV, BAJAJHFL, BAJAJHLDNG, BAJFINANCE, BALKRISIND, BALRAMCHIN, BANDHANBNK, BANKBARODA, BANKINDIA, BATAINDIA, BBOX, BDL, BEL, BELRISE, BEML, BERGEPAINT, BHARATCOAL, BHARATFORG, BHARTIARTL, BHARTIHEXA, BHEL, BIOCON, BLS, BLUESTARCO, BOSCHLTD, BPCL, BRIGADE, BRITANNIA, BSE, BSOFT, CAMS, CANBK, CANFINHOME, CANHLIFE, CAPLIPOINT, CARBORUNIV, CARTRADE, CASTROLIND, CCL, CDSL, CEATLTD, CEMPRO, CENTRALBK, CESC, CGCL, CGPOWER, CHAMBLFERT, CHENNPETRO, CHOICEIN, CHOLAFIN, CHOLAHLDNG, CIEINDIA, CIPLA, CLEAN, CLEANMAX, CMPDI, COALINDIA, COCHINSHIP, COFORGE, COHANCE, COLPAL, CONCOR, CONCORDBIO, COROMANDEL, CPPLUS, CRAFTSMAN, CREDITACC, CRISIL, CROMPTON, CUB, CUMMINSIND, CUPID, CYIENT, DABUR, DALBHARAT, DATAPATTNS, DEEPAKFERT, DEEPAKNTR, DELHIVERY, DEVYANI, DIVISLAB, DIXON, DLF, DMART, DOMS, DRREDDY, ECLERX, EICHERMOT, EIDPARRY, EIHOTEL, ELECON, ELGIEQUIP, EMAMILTD, EMCURE, EMMVEE, ENDURANCE, ENGINERSIN, ENRIN, ESCORTS, ETERNAL, EXIDEIND, FACT, FEDERALBNK, FINCABLES, FIRSTCRY, FIVESTAR, FLUOROCHEM, FORCEMOT, FORTIS, FRACTAL, FSL, GABRIEL, GAIL, GALLANTT, GESHIP, GICRE, GILLETTE, GLAND, GLAXO, GLENMARK, GMDCLTD, GMRAIRPORT, GODFRYPHLP, GODREJCP, GODREJIND, GODREJPROP, GPIL, GRANULES, GRAPHITE, GRASIM, GRAVITA, GROWW, GRSE, GVT&D, HAL, HAVELLS, HBLENGINE, HCLTECH, HDBFS, HDFCAMC, HDFCBANK, HDFCLIFE, HEGAM, HEROMOTOCO, HEXT, HFCL, HINDALCO, HINDCOPPER, HINDPETRO, HINDUNILVR, HINDZINC, HOMEFIRST, HONASA, HONAUT, HSCL, HUDCO, HYUNDAI, ICICIAMC, ICICIBANK, ICICIGI, ICICILIFE, IDBI, IDEA, IDFCFIRSTB, IEX, IFCI, IGIL, IGL, IIFL, IKS, INDHOTEL, INDIACEM, INDIAMART, INDIANB, INDIGO, INDUSINDBK, INDUSTOWER, INFY, INOXINDIA, INOXWIND, INTELLECT, IOB, IOC, IPCALAB, IRB, IRCON, IRCTC, IREDA, IRFC, ITC, ITCHOTELS, ITI, J&KBANK, JAINREC, JBMA, JINDALSAW, JINDALSTEL, JIOFIN, JKCEMENT, JKTYRE, JMFINANCIL, JPPOWER, JSL, JSWCEMENT, JSWENERGY, JSWINFRA, JSWSTEEL, JUBLFOOD, JUBLINGREA, JWL, JYOTICNC, KAJARIACER, KALYANKJIL, KARURVYSYA, KAYNES, KEC, KEI, KFINTECH, KIMS, KIRLOSBROS, KIRLOSENG, KOTAKBANK, KPIL, KPITTECH, KPRMILL, KSB, LALPATHLAB, LAURUSLABS, LEMONTREE, LENSKART, LGEINDIA, LICHSGFIN, LICI, LINDEINDIA, LLOYDSME, LODHA, LT, LTF, LTFOODS, LTM, LTTS, LUPIN, M&M, M&MFIN, MAHABANK, MANAPPURAM, MANKIND, MARICO, MARUTI, MAXHEALTH, MAZDOCK, MCX, MEDANTA, MEESHO, MFSL, MGL, MINDACORP, MMTC, MOTHERSON, MOTILALOFS, MPHASIS, MRF, MRPL, MSUMI, MTARTECH, MUTHOOTFIN, NAM-INDIA, NATCOPHARM, NATIONALUM, NAUKRI, NAVA, NAVINFLUOR, NBCC, NCC, NESTLEIND, NETWEB, NEULANDLAB, NH, NHPC, NIACL, NLCINDIA, NMDC, NSLNISP, NTPC, NTPCGREEN, NUVAMA, NUVOCO, NYKAA, OBEROIRLTY, OFSS, OIL, OLAELEC, OLECTRA, ONESOURCE, ONGC, PAGEIND, PARADEEP, PATANJALI, PAYTM, PCBL, PERSISTENT, PETRONET, PFC, PFOCUS, PGEL, PHOENIXLTD, PIDILITIND, PIIND, PINELABS, PIRAMALFIN, PNB, PNBHOUSING, POLICYBZR, POLYCAB, POLYMED, POONAWALLA, POWERGRID, POWERINDIA, PPLPHARMA, PREMIERENE, PRESTIGE, PRIVISCL, PTCIL, PVRINOX, PWL, RADICO, RAILTEL, RAINBOW, RAMCOCEM, RBLBANK, RECLTD, REDINGTON, RELIANCE, RHIM, RITES, RKFORGE, RPOWER, RRKABEL, RUBICON, RVNL, SAGILITY, SAIL, SAILIFE, SAMMAANCAP, SANSERA, SARDAEN, SBICARD, SBILIFE, SBIN, SCHAEFFLER, SCHNEIDER, SCI, SHREECEM, SHRIPISTON, SHRIRAMFIN, SHYAMMETL, SIEMENS, SIGNATURE, SJVN, SOBHA, SOLARINDS, SONACOMS, SRF, STARHEALTH, STLTECH, SUMICHEM, SUNDARMFIN, SUNPHARMA, SUNTV, SUPREMEIND, SUZLON, SWANCORP, SWIGGY, SYNGENE, SYRMA, TARIL, TATACAP, TATACHEM, TATACOMM, TATACONSUM, TATAELXSI, TATAINVEST, TATAPOWER, TATASTEEL, TATATECH, TBOTEK, TCS, TDPOWERSYS, TECHM, TECHNOE, TEGA, TEJASNET, TENNIND, THANGAMAYL, THERMAX, TIINDIA, TIMKEN, TITAGARH, TITAN, TMCV, TMPV, TORNTPHARM, TORNTPOWER, TRENT, TRIDENT, TRITURBINE, TTML, TVSMOTOR, UBL, UCOBANK, ULTRACEMCO, UNIONBANK, UNITDSPR, UNOMINDA, UPL, URBANCO, USHAMART, UTIAMC, VAML, VBL, VEDL, VEDPOWER, VIJAYA, VISL, VMM, VOGL, VOLTAS, VTL, WAAREEENER, WELCORP, WELSPUNLIV, WHIRLPOOL, WIPRO, WOCKPHARMA, YESBANK, ZEEL, ZENSARTECH, ZENTEC, ZFCVINDIA, ZYDUSLIFE, ZYDUSWELL'''.split(', ')


def extract_ticker(raw, ticker):
    """Read either common yfinance column layout, or return None for a missing stock."""
    if raw is None or raw.empty:
        return None
    if isinstance(raw.columns, pd.MultiIndex):
        for level in range(raw.columns.nlevels):
            if ticker in raw.columns.get_level_values(level):
                try:
                    return raw.xs(ticker, axis=1, level=level, drop_level=True)
                except KeyError:
                    return None
        return None
    return raw if 'Close' in raw.columns else None


def candle_row(symbol, minutes, now):
    """Use only finished bars and immediately adjacent minutes in the same session."""
    if minutes is None or minutes.empty or 'Close' not in minutes:
        return None
    s = pd.to_numeric(minutes['Close'], errors='coerce').dropna()
    if s.empty:
        return None
    index = pd.DatetimeIndex(s.index)
    if index.tz is None:          # Never guess an exchange timezone.
        return None
    s.index = index.tz_convert(IST)
    s = s[~s.index.duplicated(keep='last')].sort_index()
    now = pd.Timestamp(now)
    if now.tzinfo is None:
        raise ValueError('Clock must be timezone-aware')
    now = now.tz_convert(IST)
    s = s[(s.index + pd.Timedelta(minutes=1) <= now) &
          (s.index.time >= dt_time(9, 15)) & (s.index.time <= dt_time(15, 29)) & (s > 0)]
    if s.empty:
        return None
    candle_time = s.index[-1]
    latest = float(s.iloc[-1])
    previous = candle_time - pd.Timedelta(minutes=1)
    change = None
    if previous in s.index and previous.date() == candle_time.date():
        prev = float(s.loc[previous])
        if prev > 0:
            change = (latest / prev - 1.0) * 100.0
    # CHANGED: show only HH:MM (no date / no month), 24-hour India time.
    return {'symbol': symbol, 'close': latest,
            'candle': candle_time.strftime('%H:%M'),
            'candle_iso': candle_time.isoformat(), 'change': change}


def fetch_snapshot():
    """Fetch only minute data. Batch failure never stops the next batch."""
    rows, errors = [], []
    for start in range(0, len(SYMBOLS), BATCH_SIZE):
        batch = SYMBOLS[start:start + BATCH_SIZE]
        tickers = [symbol + '.NS' for symbol in batch]
        try:
            data = yf.download(tickers=tickers, period='1d', interval='1m',
                               group_by='ticker', threads=True, progress=False,
                               auto_adjust=False, timeout=DOWNLOAD_TIMEOUT)
        except Exception as exc:
            errors.append(f'Batch {start//BATCH_SIZE+1}: {type(exc).__name__}')
            continue
        # Evaluate completion after network call. Do not include the still-forming bar.
        now = pd.Timestamp.now(tz=IST)
        for symbol, ticker in zip(batch, tickers):
            try:
                result = candle_row(symbol, extract_ticker(data, ticker), now)
                if result:
                    rows.append(result)
            except Exception:
                errors.append(symbol)
    return rows, errors


class SharedScanner:
    """A single background worker, shared across browser sessions in this process.

    It keeps the last completed snapshot visible while fetching a replacement.
    Streamlit is never called from this background thread.
    """
    def __init__(self):
        self.lock = Lock()
        self.rows = []
        self.errors = []
        self.completed_at = None
        self.next_refresh = time.time()  # Initial download starts immediately.
        self.failure = False
        self.last_seen = time.monotonic()
        Thread(target=self.loop, daemon=True, name='nifty-research-worker').start()

    def visit(self):
        with self.lock:
            self.last_seen = time.monotonic()

    def snapshot(self):
        with self.lock:
            return list(self.rows), list(self.errors), self.completed_at, self.next_refresh, self.failure

    def loop(self):
        while True:
            with self.lock:
                active = time.monotonic() - self.last_seen < 90
                due = self.next_refresh is not None and time.time() >= self.next_refresh
                if active and due:
                    started_at = time.time()
                    self.next_refresh = None  # In progress; don't invent a countdown.
            if not (active and due):
                time.sleep(1)
                continue
            try:
                rows, errors = fetch_snapshot()
            except Exception as exc:
                rows, errors = [], [type(exc).__name__]
            with self.lock:
                if rows:
                    self.rows = rows
                    self.completed_at = time.time()
                # On total failure keep old table, clearly identify it as such.
                self.failure = not bool(rows)
                self.errors = errors
                self.next_refresh = max(started_at + REFRESH_SECONDS, time.time() + 5)


@st.cache_resource(show_spinner=False)
def get_scanner():
    return SharedScanner()


def heading_html(next_refresh):
    # The countdown runs in the browser once per second. It is corrected from the
    # actual worker schedule each time the header fragment refreshes.
    target = 'null' if next_refresh is None else str(int(next_refresh * 1000))
    name = html.escape(SCREENER_NAME)
    colour = html.escape(TITLE_COLOUR, quote=True)
    return f'''<!doctype html><html><head><meta name="viewport" content="width=device-width,initial-scale=1">
    <style>body{{margin:0;background:#131722;color:#d1d4dc;font:15px system-ui,sans-serif}}
    h1{{color:{colour};font-size:clamp(23px,4vw,34px);line-height:1.15;margin:2px 0 10px;font-weight:800;letter-spacing:.015em}}
    .time{{color:#e0e4eb;display:flex;flex-wrap:wrap;gap:8px 24px;align-items:baseline}}
    strong{{color:#edf0f4;font-variant-numeric:tabular-nums}}
    #count{{color:{colour};font-size:22px;font-weight:800;min-width:2ch;display:inline-block}}</style></head><body>
    <h1>{name}</h1><div class="time"><span>Current time: <strong id="clock">--</strong> IST</span>
    <span>Next refresh in <strong id="count">--</strong>s</span></div>
    <script>const target={target}; function tick() {{
      document.getElementById('clock').textContent = new Intl.DateTimeFormat('en-IN',{{timeZone:'Asia/Kolkata',hour:'2-digit',minute:'2-digit',second:'2-digit',hour12:true}}).format(new Date());
      const n=target===null ? null : Math.max(0, Math.ceil((target-Date.now())/1000));
      document.getElementById('count').textContent = n===null ? '—' : n;
    }} tick();setInterval(tick,1000);</script></body></html>'''


def table_html(rows, mode):
    """Simple HTML table: real bold, centered headers and clickable sorting.
    Sort choice is saved in the browser session when the table refreshes.
    Column order: Symbol, Price, 1M %, Candle.
    """
    data = json.dumps(rows, ensure_ascii=True, allow_nan=False).replace('<', '\\u003c')
    mode_json = json.dumps(mode)
    return '''<!doctype html><html><head><meta name="viewport" content="width=device-width,initial-scale=1">
<style>
*{box-sizing:border-box}body{margin:0;background:#131722;color:#d1d4dc;font:14px system-ui,sans-serif}
.wrap{overflow:auto;max-height:620px;border:1px solid #2a2e39;border-radius:7px}
table{border-collapse:collapse;width:100%;min-width:500px;font-variant-numeric:tabular-nums}
th{position:sticky;top:0;background:#242938;color:#f3f4f5;font-size:14px;font-weight:800;text-align:center;z-index:2;border-bottom:1px solid #38404d;padding:0}
th button{all:unset;box-sizing:border-box;display:block;width:100%;padding:13px 6px;cursor:pointer;text-align:center}
th button:focus-visible{outline:2px solid #f3b65a;outline-offset:-3px}
td{text-align:center;border-bottom:1px solid #2a2e39;padding:10px 5px;white-space:nowrap}
tr:hover td{background:#1e2530}.pos{color:#1fcaa5}.neg{color:#fb6974}.dim{color:#939aa7}
.empty{text-align:center;padding:24px;color:#b5bac5}</style></head><body>
<div class="wrap" id="wrap"><table><thead><tr>
<th><button data-col="symbol">Symbol ⇅</button></th><th><button data-col="close">Price ⇅</button></th>
<th><button data-col="change">1M % ⇅</button></th><th><button data-col="candle_iso">Candle ⇅</button></th>
</tr></thead><tbody id="body"></tbody></table><div class="empty" id="empty" hidden>No matching rows.</div></div>
<script>
const rows=__DATA__, mode=__MODE__, key='nifty500-sort-v1';
let state={col:'change',dir:mode==='1m Losers'?'asc':'desc',mode:mode};
try{const old=JSON.parse(sessionStorage.getItem(key));if(old&&old.mode===mode)state=old;}catch(e){}
function render(){
 const filtered=rows.filter(r=>mode==='All'||(r.change!==null&&(mode==='1m Gainers'?r.change>0:r.change<0)));
 filtered.sort((a,b)=>{let x=a[state.col],y=b[state.col];if(x===null)return y===null?0:1;if(y===null)return -1;
  let cmp=typeof x==='number'?x-y:String(x).localeCompare(String(y));return state.dir==='asc'?cmp:-cmp;});
 const body=document.getElementById('body');body.replaceChildren();
 for(const r of filtered){const tr=document.createElement('tr');
  const vals=[r.symbol,'₹'+r.close.toFixed(2),r.change===null?'—':(r.change>0?'+':'')+r.change.toFixed(2)+'%',r.candle];
  vals.forEach((v,i)=>{const td=document.createElement('td');td.textContent=v;if(i===2)td.className=r.change===null||r.change===0?'dim':(r.change>0?'pos':'neg');tr.appendChild(td)});body.appendChild(tr)}
 document.getElementById('empty').hidden=filtered.length>0;
 document.querySelectorAll('th button').forEach(b=>{const col=b.dataset.col;b.textContent=b.textContent.replace(/ [⇅↑↓]$/,'')+' '+(state.col===col?(state.dir==='asc'?'↑':'↓'):'⇅')});
}
const wrap=document.getElementById('wrap');
try{wrap.scrollTop=Number(sessionStorage.getItem('nifty500-scroll-v1')||0)}catch(e){}
wrap.addEventListener('scroll',()=>{try{sessionStorage.setItem('nifty500-scroll-v1',String(wrap.scrollTop))}catch(e){}});
document.querySelectorAll('th button').forEach(b=>b.addEventListener('click',()=>{
 const col=b.dataset.col;state.dir=state.col===col&&state.dir==='desc'?'asc':'desc';state.col=col;
 try{sessionStorage.setItem(key,JSON.stringify(state))}catch(e){}render();}));render();
</script></body></html>'''.replace('__DATA__',data).replace('__MODE__',mode_json)


def main():
    st.set_page_config(page_title=SCREENER_NAME, layout='wide', initial_sidebar_state='collapsed')
    st.markdown('''<style>
    .stApp{background:#131722;color:#d1d4dc}.block-container{padding-top:3.1rem;max-width:1200px}
    div[data-testid="stStatusWidget"]{display:none!important}
    div[data-testid="stDecoration"]{display:none}
    </style>''', unsafe_allow_html=True)
    scanner = get_scanner()

    @st.fragment(run_every=5)
    def header_fragment():
        scanner.visit()
        _, _, _, next_refresh, _ = scanner.snapshot()
        components.html(heading_html(next_refresh), height=90, scrolling=False)

    @st.fragment(run_every=5)
    def table_fragment():
        scanner.visit()
        rows, errors, completed_at, _, failure = scanner.snapshot()
        mode = st.radio('View', ['All', '1m Gainers', '1m Losers'], horizontal=True,
                        label_visibility='collapsed', key='mode')
        if not rows:
            st.info('No completed candles are available yet. If this continues, Yahoo may be unavailable or rate-limiting.')
            return
        if failure:
            st.warning('Latest download failed. This is the previous saved table, so its candles may be old.')
        elif len(rows) < len(SYMBOLS):
            st.caption(f'{len(rows)} of {len(SYMBOLS)} symbols returned usable candles; the rest are not shown.')
        components.html(table_html(rows, mode), height=640, scrolling=False)
        st.caption('Research only: Yahoo candles can be missing or delayed. Check each candle time and verify prices with your broker. The refresh timer is not proof of live market data.')

    header_fragment()
    table_fragment()


if __name__ == '__main__':
    main()