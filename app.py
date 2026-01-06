import streamlit as st
import requests
from bs4 import BeautifulSoup
import time
import re

# --- 1. CONFIGURATION ---
st.set_page_config(
    page_title="QUANTUM | Global Macro",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 2. TITANIUM UI THEME (V6.0) ---
st.markdown("""
    <style>
        /* Import Professional Fonts */
        @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&family=Inter:wght@300;400;600&display=swap');
        
        /* Global Reset */
        .stApp { background-color: #0d1117; color: #e6edf3; font-family: 'Inter', sans-serif; }
        [data-testid="stSidebar"] { background-color: #010409; border-right: 1px solid #30363d; }
        
        /* Headers */
        h1, h2, h3 { color: #f0f6fc !important; font-family: 'Inter', sans-serif; font-weight: 600; letter-spacing: -0.5px; }
        
        /* Buttons */
        .stButton>button {
            width: 100%; padding: 12px 20px; border-radius: 6px; font-weight: 600; font-size: 14px;
            transition: all 0.2s ease; border: 1px solid rgba(255,255,255,0.1);
        }
        
        /* The Report Container */
        .terminal-card {
            background-color: #161b22; 
            border: 1px solid #30363d; 
            border-radius: 8px;
            padding: 30px; 
            margin-top: 15px; 
            box-shadow: 0 4px 24px rgba(0,0,0,0.2);
        }
        
        /* The Text Content */
        .report-content {
            font-family: 'Inter', sans-serif;
            font-size: 15px;
            line-height: 1.8;
            color: #c9d1d9;
            white-space: pre-wrap; 
        }
        
        /* Pair Tags Styling */
        .pair-tag {
            color: #79c0ff;
            font-family: 'JetBrains Mono', monospace;
            font-weight: bold;
            font-size: 14px;
        }
        
        /* Report Headers */
        .report-content h3 {
            margin-top: 25px;
            margin-bottom: 15px;
            font-size: 17px;
            border-bottom: 1px solid #21262d;
            padding-bottom: 8px;
            color: #f0f6fc;
            text-transform: uppercase;
            letter-spacing: 1px;
        }
    </style>
""", unsafe_allow_html=True)

# --- 3. SIDEBAR ---
with st.sidebar:
    st.title("💠 QUANTUM")
    st.caption("Global Macro Unit v6.0")
    st.markdown("---")
    api_key = st.text_input("Google API Key", type="password")
    
    st.markdown("---")
    st.subheader("⚙️ Active Protocol")
    col_a, col_b = st.columns(2)
    col_a.metric("BTC Scan", "DEEP DIVE")
    col_b.metric("FX Scan", "7 MAJORS")

# --- 4. INTELLIGENCE SOURCES ---
BTC_SOURCES = [
    "https://cointelegraph.com/tags/bitcoin",
    "https://u.today/bitcoin-news",
    "https://cryptonews.com/news/bitcoin-news/",
    "https://www.newsbtc.com/"
]

FX_SOURCES = [
    "https://www.fxstreet.com/news",           # The Firehose (Everything)
    "https://www.forexlive.com/",              # Real-time sentiment
    "https://www.dailyfx.com/market-news",     # Analysis
    "https://www.reuters.com/markets/currencies/" # Institutional Macro
]

# --- 5. CORE LOGIC ---
def get_valid_model(api_key):
    url = f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}"
    try:
        response = requests.get(url)
        data = response.json()
        if 'error' in data: return None, data['error']['message']
        valid_models = [m['name'] for m in data.get('models', []) if 'generateContent' in m['supportedGenerationMethods']]
        # ALWAYS use FLASH for this amount of data
        for m in valid_models:
            if 'flash' in m: return m, None
        return valid_models[0], None
    except:
        return None, "Connection Failed"

def scrape_site(url, char_limit):
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers, timeout=5)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            texts = [p.get_text() for p in soup.find_all(['h1', 'h2', 'h3', 'p', 'article'])]
            return f"[[SOURCE: {url}]]\n" + " ".join(texts)[:char_limit] + "\n\n"
        return ""
    except:
        return ""

def clean_text(text):
    text = text.replace("$", "USD ")
    text = text.replace(" *", "*")
    return text

def generate_report(data_dump, topic, mode):
    if not api_key: return "⚠️ Missing API Key"
    
    model_name, error = get_valid_model(api_key)
    if error: return f"Error: {error}"
    
    url = f"https://generativelanguage.googleapis.com/v1beta/{model_name}:generateContent?key={api_key}"
    headers = {'Content-Type': 'application/json'}
    
    # --- DYNAMIC PROMPTS ---
    if mode == "BTC":
        prompt_text = f"""
        ROLE: Chief Investment Officer (Crypto).
        TASK: Massive deep-dive report on Bitcoin.
        RULES: No LaTeX. No $ symbols. Markdown Only.
        
        RAW DATA:
        {data_dump}
        
        ---
        OUTPUT FORMAT (Markdown):
        ### ⚡️ MARKET REGIME
        (Psychology & Sentiment).
        ### 🐋 ON-CHAIN & FLOWS
        (ETF & Whale Analysis).
        ### 📊 TECHNICALS
        (Deep Chart Analysis).
        ### 🔮 VERDICT
        (Bullish/Bearish & Invalidation Level).
        """
    else: # FX MODE - 7 MAJORS
        prompt_text = f"""
        ROLE: Senior Forex Strategist.
        TASK: Produce a granular report on the 7 MAJOR PAIRS.
        RULES: No LaTeX. No $ symbols. Markdown Only.
        
        RAW DATA:
        {data_dump}
        
        ---
        OUTPUT FORMAT (Strict Markdown - Cover ALL 7):
        
        ### 🌍 MACRO CONTEXT
        (DXY Dollar Index & Risk Sentiment).
        
        ### 🇪🇺 EUR/USD
        (Bias | Drivers | Key Levels)
        
        ### 🇬🇧 GBP/USD
        (Bias | Drivers | Key Levels)
        
        ### 🇨🇦 USD/CAD
        (Bias | Oil Correlation | Levels)
        
        ### 🇯🇵 USD/JPY
        (Bias | Yield Spreads | Intervention Risk)
        
        ### 🇨🇭 USD/CHF
        (Bias | Safe Haven Flows)
        
        ### 🇦🇺 AUD/USD
        (Bias | China/Commodity Impact)
        
        ### 🇳🇿 NZD/USD
        (Bias | RBNZ Outlook)
        """
    
    payload = {"contents": [{"parts": [{"text": prompt_text}]}]}
    try:
        response = requests.post(url, headers=headers, json=payload)
        if response.status_code == 200:
            return clean_text(response.json()['candidates'][0]['content']['parts'][0]['text'])
        elif response.status_code == 429:
            return "⚠️ **RATE LIMIT:** Please wait 60 seconds."
        else:
            return f"Error: {response.text}"
    except Exception as e:
        return str(e)

# --- 6. DASHBOARD UI ---
st.title("QUANTUM TERMINAL")
st.caption("Global Market Intelligence Unit")

tab1, tab2 = st.tabs(["⚡️ BITCOIN", "🌍 FOREX (7 MAJORS)"])

with tab1:
    if st.button("RUN DEEP BTC SCAN", type="primary"):
        with st.status("Scanning Crypto Liquidity...", expanded=True):
            raw = ""
            bar = st.progress(0)
            for i, s in enumerate(BTC_SOURCES):
                # MAX POWER: 15,000 chars per site
                raw += scrape_site(s, 15000) 
                time.sleep(0.1) # Tiny pause to prevent rate limit
                bar.progress((i+1)/len(BTC_SOURCES))
            
            st.write("Synthesizing Report...")
            report = generate_report(raw, "Bitcoin", "BTC")
            st.session_state['btc_rep'] = report
            
    if 'btc_rep' in st.session_state:
        st.markdown(f"""<div class="terminal-card"><div class="report-content">{st.session_state['btc_rep']}</div></div>""", unsafe_allow_html=True)

with tab2:
    if st.button("RUN 7-MAJORS SCAN", type="primary"):
        with st.status("Scanning Global Order Flow...", expanded=True):
            raw = ""
            bar = st.progress(0)
            for i, s in enumerate(FX_SOURCES):
                # INCREASED POWER: 10,000 chars per site to catch NZD/CHF news
                st.write(f"Ingesting: {s.split('/')[2]}...")
                raw += scrape_site(s, 10000)
                time.sleep(0.5) # Safety pause for heavier load
                bar.progress((i+1)/len(FX_SOURCES))
            
            st.write("Triangulating Major Pairs...")
            report = generate_report(raw, "Forex", "FX")
            st.session_state['fx_rep'] = report

    if 'fx_rep' in st.session_state:
        st.markdown(f"""<div class="terminal-card"><div class="report-content">{st.session_state['fx_rep']}</div></div>""", unsafe_allow_html=True)