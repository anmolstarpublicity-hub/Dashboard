import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os
import html
import logging
from datetime import datetime, timedelta
from streamlit_autorefresh import st_autorefresh
import streamlit.components.v1 as components

logging.basicConfig(level=logging.ERROR, format='%(asctime)s %(levelname)s %(message)s')

# --- SETTINGS ---
# amazonq-ignore-next-line
ACTIVITY_INTERVAL_SEC = 60
ACTIVITY_LOG_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "activity.log")

# PAGE CONFIG
# amazonq-ignore-next-line
st.set_page_config(layout="wide", page_title="Spy | Monitoring Tool", page_icon="📊")
# amazonq-ignore-next-line
st_autorefresh(interval=60000, key="datarefresh")

# CSS STYLING — Windows 11 Mica/Acrylic
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

    html, body, [class*="css"] { font-family: 'Inter', 'Segoe UI', sans-serif; }

    /* Background */
    .stApp, html, body,
    [data-testid="stAppViewContainer"],
    [data-testid="stHeader"] {
        background: #f8f8ff !important;
        background-attachment: fixed !important;
    }

    /* Reduce top gap only via block container */
    [data-testid="stToolbar"] { padding-top: 0 !important; padding-bottom: 0 !important; }
    [data-testid="stAppViewBlockContainer"] { padding-top: 0.5rem !important; }
    [data-testid="stVerticalBlockBorderWrapper"] { padding-top: 0 !important; }
    .stMainBlockContainer { padding-top: 0.5rem !important; }

    /* Main content */
    .main .block-container {
        padding: 0.5rem 2.2rem 1.8rem 2.2rem !important;
        background: #ffffff !important;
        border-radius: 20px !important;
        border: 1px solid rgba(103,61,230,0.12) !important;
        box-shadow: 0 4px 24px rgba(103,61,230,0.08) !important;
        margin: 0 0.8rem 0.8rem 0 !important;
    }

    /* Global text */
    .stSelectbox label, .stCheckbox label, .stCheckbox span,
    .stMarkdown p, .stMarkdown h1, .stMarkdown h2, .stMarkdown h3 {
        color: #1D1D2E !important;
        text-shadow: none !important;
    }
    .stCheckbox {
        background: #f4f3ff !important;
        border-radius: 8px !important;
        padding: 4px 8px !important;
        margin-bottom: 2px !important;
        border: 1px solid rgba(103,61,230,0.15) !important;
    }
    .stSelectbox > div > div {
        background: #f4f3ff !important;
        border: 1px solid rgba(103,61,230,0.2) !important;
        color: #1D1D2E !important;
    }
    .stSelectbox > div > div > div { color: #1D1D2E !important; }

    /* Sidebar — floating card */
    section[data-testid="stSidebar"] {
        background: transparent !important;
        border: none !important;
        box-shadow: none !important;
        padding: 12px !important;
    }
    section[data-testid="stSidebar"] > div:first-child {
        background: linear-gradient(139deg, rgba(52,57,70,1) 0%, rgba(54,44,58,1) 100%) !important;
        border-radius: 18px !important;
        border: 1.5px solid #42434a !important;
        box-shadow: 0 8px 32px rgba(0,0,0,0.45) !important;
        padding: 0 0.8rem !important;
        margin: 4px !important;
        min-height: calc(100vh - 24px) !important;
    }
    [data-testid="stSidebarContent"] { padding-top: 0 !important; }

    /* Hide the sidebar collapse/minimize button */
    [data-testid="collapsedControl"],
    [data-testid="stSidebarCollapseButton"] {
        display: none !important;
    }

    /* Sidebar nav buttons — Uiverse pill style */
    section[data-testid="stSidebar"] .stButton button {
        width: 100% !important;
        height: 38px !important;
        min-height: 38px !important;
        max-height: 38px !important;
        font-size: 12px !important;
        font-weight: 600 !important;
        border-radius: 50px !important;
        background: #ffffff !important;
        color: #1D1D2E !important;
        border: 0 !important;
        margin-bottom: 4px !important;
        letter-spacing: 1.5px !important;
        text-transform: uppercase !important;
        box-shadow: rgb(0 0 0 / 5%) 0 0 8px !important;
        text-shadow: none !important;
        transition: all 0.5s ease !important;
    }
    section[data-testid="stSidebar"] .stButton button p {
        color: #1D1D2E !important;
        font-size: 12px !important;
        letter-spacing: 1.5px !important;
        text-transform: uppercase !important;
        font-weight: 600 !important;
    }
    section[data-testid="stSidebar"] .stButton button:hover {
        letter-spacing: 3px !important;
        background: hsl(261deg 80% 48%) !important;
        color: #ffffff !important;
        box-shadow: rgb(93 24 220) 0px 7px 29px 0px !important;
    }
    section[data-testid="stSidebar"] .stButton button:hover p { color: #ffffff !important; letter-spacing: 3px !important; }
    section[data-testid="stSidebar"] .stButton button:active {
        letter-spacing: 3px !important;
        background: hsl(261deg 80% 48%) !important;
        color: #ffffff !important;
        box-shadow: rgb(93 24 220) 0px 0px 0px 0px !important;
        transform: translateY(10px) !important;
        transition: 100ms !important;
    }
    section[data-testid="stSidebar"] .stButton button:active p { color: #ffffff !important; }
    section[data-testid="stSidebar"] hr {
        margin: 0.3rem 0 !important;
    }
    section[data-testid="stSidebar"] .stDateInput label {
        color: #7e8590 !important;
        font-size: 11px !important;
        font-weight: 600 !important;
        letter-spacing: 1px !important;
        text-transform: uppercase !important;
        text-shadow: none !important;
    }
    section[data-testid="stSidebar"] .stDateInput input,
    section[data-testid="stSidebar"] [data-baseweb="base-input"] input {
        color: #c8ccd4 !important;
        -webkit-text-fill-color: #c8ccd4 !important;
        caret-color: #c8ccd4 !important;
        font-size: 14px !important;
        font-weight: 500 !important;
        background: transparent !important;
        border: none !important;
        outline: none !important;
        box-shadow: none !important;
        text-shadow: none !important;
    }
    section[data-testid="stSidebar"] [data-baseweb="input"],
    section[data-testid="stSidebar"] [data-baseweb="base-input"],
    section[data-testid="stSidebar"] .stDateInput > div,
    section[data-testid="stSidebar"] .stDateInput > div > div {
        background: transparent !important;
        border: none !important;
        border-radius: 14px !important;
        box-shadow: none !important;
    }
    section[data-testid="stSidebar"] [data-baseweb="base-input"] > div {
        background: transparent !important;
    }

    /* Metrics */
    [data-testid="stMetric"] {
        background: #ffffff !important;
        border: 1px solid rgba(103,61,230,0.15) !important;
        border-radius: 14px !important;
        padding: 1.2rem 1.4rem !important;
        box-shadow: 0 2px 8px rgba(103,61,230,0.08) !important;
    }
    [data-testid="stMetricLabel"] { color: #673DE6 !important; font-size: 11px !important; font-weight: 600 !important; text-transform: uppercase !important; letter-spacing: 0.8px !important; }
    [data-testid="stMetricValue"] { color: #1D1D2E !important; font-size: 28px !important; font-weight: 700 !important; }

    /* Dataframes */
    [data-testid="stDataFrame"] {
        border-radius: 12px !important;
        overflow: hidden !important;
        border: 1px solid rgba(103,61,230,0.15) !important;
        box-shadow: 0 2px 8px rgba(103,61,230,0.06) !important;
    }

    /* Chart box */
    [data-testid="stPlotlyChart"] > div {
        border-radius: 12px !important;
        overflow: hidden !important;
        border: 1px solid rgba(103,61,230,0.15) !important;
        box-shadow: 0 2px 8px rgba(103,61,230,0.06) !important;
    }

    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        background: #f4f3ff;
        border-radius: 10px;
        padding: 4px;
        gap: 4px;
        border: 1px solid rgba(103,61,230,0.15);
    }
    .stTabs [data-baseweb="tab"] { border-radius: 7px; color: #6b7280; font-weight: 500; font-size: 13px; }
    .stTabs [aria-selected="true"] { background: #673DE6 !important; color: #ffffff !important; font-weight: 600 !important; border: none !important; }

    /* ── Page load animations ── */
    @keyframes fadeSlideUp {
        from { opacity: 0; transform: translateY(24px); }
        to   { opacity: 1; transform: translateY(0); }
    }
    @keyframes fadeSlideLeft {
        from { opacity: 0; transform: translateX(-28px); }
        to   { opacity: 1; transform: translateX(0); }
    }
    @keyframes fadeIn {
        from { opacity: 0; }
        to   { opacity: 1; }
    }
    @keyframes scaleIn {
        from { opacity: 0; transform: scale(0.93); }
        to   { opacity: 1; transform: scale(1); }
    }

    /* Sidebar slides in from left + smooth toggle transition */
    section[data-testid="stSidebar"] {
        animation: fadeSlideLeft 0.45s cubic-bezier(0.4,0,0.2,1) both !important;
    }
    /* Main content block fades up */
    .main .block-container {
        animation: fadeSlideUp 0.5s 0.1s cubic-bezier(0.4,0,0.2,1) both !important;
    }

    /* Metrics scale in with stagger */
    [data-testid="stMetric"] {
        animation: scaleIn 0.4s cubic-bezier(0.4,0,0.2,1) both !important;
    }
    [data-testid="column"]:nth-child(1) [data-testid="stMetric"] { animation-delay: 0.15s !important; }
    [data-testid="column"]:nth-child(2) [data-testid="stMetric"] { animation-delay: 0.22s !important; }
    [data-testid="column"]:nth-child(3) [data-testid="stMetric"] { animation-delay: 0.29s !important; }
    [data-testid="column"]:nth-child(4) [data-testid="stMetric"] { animation-delay: 0.36s !important; }

    /* Charts fade up */
    [data-testid="stPlotlyChart"] { animation: fadeSlideUp 0.6s 0.2s cubic-bezier(0.4,0,0.2,1) both; }

    /* Dataframes fade in */
    [data-testid="stDataFrame"] { animation: fadeIn 0.5s 0.25s cubic-bezier(0.4,0,0.2,1) both; }

    /* Markdown blocks (cards/headers) slide up */
    [data-testid="stMarkdownContainer"] > div { animation: fadeSlideUp 0.45s 0.08s cubic-bezier(0.4,0,0.2,1) both; }

    /* Tabs fade in */
    .stTabs { animation: fadeIn 0.4s 0.2s cubic-bezier(0.4,0,0.2,1) both; }

    /* Toolbar / header */
    [data-testid="stToolbar"] button,
    [data-testid="stToolbar"] button:hover,
    header button,
    header button:hover {
        background: none !important;
        background-image: none !important;
        border: none !important;
        box-shadow: none !important;
        text-shadow: none !important;
        min-height: unset !important;
        height: unset !important;
        width: unset !important;
        border-radius: 4px !important;
        padding: 4px !important;
        transform: none !important;
        color: #64748B !important;
        white-space: nowrap !important;
    }
    header[data-testid="stHeader"], [data-testid="stToolbar"] {
        background: transparent !important;
        border-bottom: none !important;
        box-shadow: none !important;
    }

    /* Employee pill buttons — hidden trigger buttons */
    [data-testid="stButton"] button {
        border-radius: 10px !important;
        font-size: 13px !important;
        font-weight: 600 !important;
        height: auto !important;
        min-height: 120px !important;
        padding: 10px 8px !important;
        line-height: 1.5 !important;
        white-space: pre-wrap !important;
        letter-spacing: 0.1px !important;
        text-transform: none !important;
    }

    /* Employee badge */
    .emp-badge {
        display: inline-flex; align-items: center; gap: 7px;
        padding: 6px 14px; border-radius: 50px;
        font-size: 13px; font-weight: 600;
        cursor: pointer; transition: all 0.18s ease;
        text-decoration: none;
    }
    .emp-badge.online { background: rgba(103,61,230,0.1); color: #673DE6; border: 1px solid rgba(103,61,230,0.25); }
    .emp-badge.offline { background: #f4f3ff; color: #6b7280; border: 1px solid rgba(103,61,230,0.12); }
    .emp-badge .dot { width: 8px; height: 8px; border-radius: 50%; flex-shrink: 0; }
    .emp-badge.online .dot { background: #673DE6; box-shadow: 0 0 6px rgba(103,61,230,0.5); }
    .emp-badge.offline .dot { background: #9ca3af; }
</style>
""", unsafe_allow_html=True)

# HELPERS
def _js_escape(s):
    """Escape a string for safe embedding inside a JS single-quoted string."""
    return s.replace('\\', '\\\\').replace("'", "\\'").replace('"', '\\"').replace('<', '\\x3c').replace('>', '\\x3e')

def format_time(units):
    total_seconds = units * ACTIVITY_INTERVAL_SEC
    h = int(total_seconds // 3600)
    m = int((total_seconds % 3600) // 60)
    return f"{h}h {m}m"

@st.cache_data(ttl=10)
def load_live_data():
    path = ACTIVITY_LOG_PATH
    if not os.path.exists(path): return pd.DataFrame()
    try:
        df = pd.read_csv(path)
        df['Timestamp'] = pd.to_datetime(df['Timestamp'])
        df['Duration'] = pd.to_numeric(df['Duration'], errors='coerce').fillna(1)
        def process_entry(val):
            v = str(val).lower()
            browsers = ['chrome','edge','firefox','brave']
            is_web = any(b in v for b in browsers) or '.com' in v
            if is_web:
                parts = v.split(' - ')
                return (parts[0] if len(parts)>1 else v).strip(), 'Website'
            return val, 'Application'
        processed = df['App/Website'].apply(process_entry)
        df['Clean Name'] = [p[0] for p in processed]
        df['Category'] = [p[1] for p in processed]
        df['Type'] = df['Clean Name'].apply(lambda x:'Idle' if any(i in str(x).lower() for i in ['idle','locked']) else 'Working')
        return df
    except Exception as e:
        logging.error("Failed to load activity log: %s", e)
        return pd.DataFrame()

# SESSION STATE
if 'nav_target' not in st.session_state: st.session_state.nav_target = "Dashboard Home"
if 'selected_emp' not in st.session_state: st.session_state.selected_emp = None
if 'filter_status' not in st.session_state: st.session_state.filter_status = "All"

df_raw = load_live_data()

# SIDEBAR
with st.sidebar:
    st.markdown("""
        <div style='padding:0.2rem 0.4rem 1.2rem 0.4rem;border-bottom:1.5px solid #42434a;margin-bottom:1rem;'>
            <div style='display:flex;align-items:center;justify-content:space-between;'>
                <div style='display:flex;align-items:center;gap:10px;'>
                    <div style='width:36px;height:36px;border-radius:10px;background:rgba(83,83,255,0.2);display:flex;align-items:center;justify-content:center;font-size:18px;box-shadow:0 4px 12px rgba(83,83,255,0.3);border:1px solid #42434a;'>🕵️</div>
                    <div><div style='font-size:18px;font-weight:800;color:#ffffff;letter-spacing:-0.5px;line-height:1.1;'>Spy</div>
                    <div style='font-size:10px;color:#7e8590;font-weight:600;letter-spacing:1.5px;text-transform:uppercase;'>Monitoring Tool</div></div>
                </div>
                <label id='sb-hamburger-label' style='position:relative;width:36px;height:36px;cursor:pointer;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:7px;transition:transform 0.35s cubic-bezier(0.4,0,0.2,1);flex-shrink:0;'>
                    <div id='hbar1' style='width:22px;height:3px;background:rgb(253,255,243);border-radius:5px;transition:transform 0.35s cubic-bezier(0.4,0,0.2,1),opacity 0.25s ease;transform-origin:50% 50%;'></div>
                    <div id='hbar2' style='width:22px;height:3px;background:rgb(253,255,243);border-radius:5px;transition:transform 0.35s cubic-bezier(0.4,0,0.2,1),opacity 0.25s ease;transform-origin:50% 50%;'></div>
                    <div id='hbar3' style='width:22px;height:3px;background:rgb(253,255,243);border-radius:5px;transition:transform 0.35s cubic-bezier(0.4,0,0.2,1),opacity 0.25s ease;transform-origin:50% 50%;'></div>
                </label>
            </div>
        </div>
    """, unsafe_allow_html=True)
    components.html("""
    <script>
    (function(){
        // inject CSS for sidebar transitions
        if (!window.parent.document.getElementById('sb-anim-style')) {
            var s = window.parent.document.createElement('style');
            s.id = 'sb-anim-style';
            s.textContent = `
                section[data-testid="stSidebar"] {
                    transition: transform 0.42s cubic-bezier(0.4,0,0.2,1) !important,
                                opacity 0.35s ease !important,
                                width 0.42s cubic-bezier(0.4,0,0.2,1) !important,
                                min-width 0.42s cubic-bezier(0.4,0,0.2,1) !important;
                    will-change: transform, opacity, width;
                }
                section[data-testid="stSidebar"].sb-hidden {
                    transform: translateX(-115%) !important;
                    opacity: 0 !important;
                    width: 0px !important;
                    min-width: 0px !important;
                    pointer-events: none !important;
                    overflow: hidden !important;
                }
                section[data-testid="stSidebar"].sb-opening {
                    transition: transform 2.2s cubic-bezier(0.16,1,0.3,1) !important,
                                opacity 1.8s ease !important,
                                width 2.2s cubic-bezier(0.16,1,0.3,1) !important,
                                min-width 2.2s cubic-bezier(0.16,1,0.3,1) !important;
                }
            `;
            window.parent.document.head.appendChild(s);
        }

        function init() {
            var sb = window.parent.document.querySelector('section[data-testid="stSidebar"]');
            if (!sb) { setTimeout(init, 200); return; }
            var label = sb.querySelector('#sb-hamburger-label');
            if (!label) { setTimeout(init, 200); return; }
            var bar1 = sb.querySelector('#hbar1');
            var bar2 = sb.querySelector('#hbar2');
            var bar3 = sb.querySelector('#hbar3');
            if (label._sbInit) return;
            label._sbInit = true;
            var open = true;

            // create float button
            if (!window.parent.document.getElementById('sb-float-btn')) {
                var floatBtn = window.parent.document.createElement('div');
                floatBtn.id = 'sb-float-btn';
                floatBtn.style.cssText = 'position:fixed;top:20px;left:12px;z-index:999999;width:36px;height:36px;cursor:pointer;display:none;flex-direction:column;align-items:center;justify-content:center;gap:7px;background:linear-gradient(139deg,rgba(52,57,70,1) 0%,rgba(54,44,58,1) 100%);border-radius:10px;border:1.5px solid #42434a;box-shadow:0 4px 16px rgba(0,0,0,0.4);padding:7px;box-sizing:border-box;opacity:0;transform:scale(0.6) translateX(-16px);transition:opacity 0.3s ease,transform 0.35s cubic-bezier(0.34,1.56,0.64,1);';
                floatBtn.innerHTML = '<div style="width:100%;height:3px;background:rgb(253,255,243);border-radius:5px;"></div><div style="width:100%;height:3px;background:rgb(253,255,243);border-radius:5px;"></div><div style="width:100%;height:3px;background:rgb(253,255,243);border-radius:5px;"></div>';
                window.parent.document.body.appendChild(floatBtn);
                floatBtn.addEventListener('click', function(){
                    if (open) return;
                    open = true;
                    // hide float btn
                    floatBtn.style.opacity = '0';
                    floatBtn.style.transform = 'scale(0.6) translateX(-16px)';
                    setTimeout(function(){ floatBtn.style.display = 'none'; }, 320);
                    // show sidebar — start bars as X then morph to hamburger mid-slide
                    bar3.style.opacity = '0'; bar3.style.transform = 'scaleX(0)';
                    bar1.style.transform = 'translateY(10px) rotate(45deg)';
                    bar2.style.transform = 'translateY(-10px) rotate(-45deg)';
                    label.style.transform = 'rotate(180deg)';
                    sb.classList.remove('sb-hidden');
                    sb.classList.add('sb-opening');
                    setTimeout(function(){ sb.classList.remove('sb-opening'); }, 2300);
                    setTimeout(function(){
                        bar1.style.transform = '';
                        bar2.style.transform = '';
                        bar3.style.transform = '';
                        bar3.style.opacity = '1';
                        label.style.transform = '';
                    }, 200);
                    setTimeout(function(){ sb.classList.remove('sb-opening'); }, 2300);
                });
            }
            var floatBtn = window.parent.document.getElementById('sb-float-btn');

            label.addEventListener('click', function(){
                open = !open;
                if (!open) {
                    // bars → X
                    bar3.style.opacity = '0'; bar3.style.transform = 'scaleX(0)';
                    bar1.style.transform = 'translateY(10px) rotate(45deg)';
                    bar2.style.transform = 'translateY(-10px) rotate(-45deg)';
                    label.style.transform = 'rotate(90deg)';
                    // hide sidebar via class
                    sb.classList.add('sb-hidden');
                    // show float btn after slide starts
                    floatBtn.style.display = 'flex';
                    setTimeout(function(){
                        floatBtn.style.opacity = '1';
                        floatBtn.style.transform = 'scale(1) translateX(0)';
                    }, 300);
                } else {
                    // bars → hamburger
                    bar1.style.transform = '';
                    bar2.style.transform = '';
                    bar3.style.transform = '';
                    bar3.style.opacity = '1';
                    label.style.transform = '';
                    // hide float btn
                    floatBtn.style.opacity = '0';
                    floatBtn.style.transform = 'scale(0.6) translateX(-16px)';
                    setTimeout(function(){ floatBtn.style.display = 'none'; }, 320);
                    // show sidebar via class
                    sb.classList.remove('sb-hidden');
                    sb.classList.add('sb-opening');
                    setTimeout(function(){ sb.classList.remove('sb-opening'); }, 2300);
                }
            });
        }
        setTimeout(init, 400);
    })();
    </script>
    """, height=0)
    _nav = st.session_state.nav_target
    if st.button("  Dashboard Home",   key="nav_dash",      use_container_width=True): st.session_state.nav_target = "Dashboard Home";  st.rerun()
    if st.button("  Employee Insights", key="nav_insights",  use_container_width=True): st.session_state.nav_target = "Employee Insights"; st.rerun()
    if st.button("  App Analytics",    key="nav_analytics", use_container_width=True): st.session_state.nav_target = "App Analytics";   st.rerun()
    if st.button("  Screenshots",       key="nav_shots",     use_container_width=True): st.session_state.nav_target = "Screenshots";      st.rerun()
    _nav_js = _js_escape(_nav)
    # amazonq-ignore-next-line
    components.html('<script>(function(){var active="' + _nav_js + '";function run(){var sb=window.parent.document.querySelector("section[data-testid=\'stSidebar\']");if(!sb){setTimeout(run,200);return;}sb.querySelectorAll(".stButton button").forEach(function(b){var t=b.innerText.trim();var keys=["Dashboard Home","Employee Insights","App Analytics","Screenshots"];var isNav=keys.some(function(k){return t.includes(k);});if(!isNav)return;var on=t.includes(active);b.style.setProperty("background",on?"hsl(261deg 80% 48%)":"#ffffff","important");b.style.setProperty("color",on?"#ffffff":"#1D1D2E","important");b.style.setProperty("box-shadow",on?"rgb(93 24 220) 0px 7px 29px 0px":"rgb(0 0 0 / 5%) 0 0 8px","important");b.style.setProperty("letter-spacing",on?"3px":"1.5px","important");b.style.setProperty("border","0","important");var p=b.querySelector("p");if(p){p.style.setProperty("color",on?"#ffffff":"#1D1D2E","important");p.style.setProperty("letter-spacing",on?"3px":"1.5px","important");}});}setTimeout(run,300);})();</script>', height=0)
    st.divider()
    _min_date = df_raw['Timestamp'].dt.date.min() if not df_raw.empty else datetime.now().date()
    _max_date = df_raw['Timestamp'].dt.date.max() if not df_raw.empty else datetime.now().date()
    if 'd_start' not in st.session_state: st.session_state.d_start = _min_date
    if 'd_end' not in st.session_state: st.session_state.d_end = _max_date
    d_start = st.date_input("From", st.session_state.d_start, key="date_from")
    d_end = st.date_input("To", st.session_state.d_end, key="date_to")
    st.session_state.d_start = d_start
    st.session_state.d_end = d_end
    components.html("""
    <script>
    function styleDateInputs() {
        const sidebar = window.parent.document.querySelector('section[data-testid="stSidebar"]');
        if (!sidebar) return;
        sidebar.querySelectorAll('.stDateInput').forEach(wrapper => {
            const label = wrapper.querySelector('label');
            if (label && !label.dataset.ps) {
                label.dataset.ps = '1';
                label.style.cssText = 'display:block;font-size:10px;font-weight:700;color:#a78bfa;letter-spacing:2px;text-transform:uppercase;margin-bottom:5px;padding-left:2px;';
            }
            const inp_wrap = wrapper.querySelector('[data-baseweb="input"]');
            if (!inp_wrap || inp_wrap.dataset.ps) return;
            inp_wrap.dataset.ps = '1';
            inp_wrap.style.cssText = 'padding:2px;border-radius:14px;background:linear-gradient(135deg,rgba(103,61,230,0.6),rgba(83,83,255,0.4),rgba(167,139,250,0.5));transition:all 0.3s ease;display:block;';
            const base = inp_wrap.querySelector('[data-baseweb="base-input"]');
            if (base) {
                base.style.setProperty('background', 'rgba(28,25,40,0.92)', 'important');
                base.style.setProperty('border', 'none', 'important');
                base.style.setProperty('border-radius', '12px', 'important');
                base.style.setProperty('height', '40px', 'important');
                base.style.setProperty('min-height', '40px', 'important');
                base.style.setProperty('padding', '0 10px', 'important');
                base.style.setProperty('display', 'flex', 'important');
                base.style.setProperty('align-items', 'center', 'important');
                base.style.setProperty('gap', '8px', 'important');
                base.querySelectorAll('div').forEach(d => d.style.setProperty('background', 'transparent', 'important'));
                if (!base.querySelector('.cal-icon')) {
                    const ic = document.createElement('span');
                    ic.className = 'cal-icon';
                    ic.style.cssText = 'display:flex;align-items:center;flex-shrink:0;opacity:0.7;';
                    ic.innerHTML = '<svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="#a78bfa" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="4" width="18" height="18" rx="3"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/></svg>';
                    base.insertBefore(ic, base.firstChild);
                }
                const inp = base.querySelector('input');
                if (inp) {
                    inp.style.setProperty('color', '#e2e8f0', 'important');
                    inp.style.setProperty('-webkit-text-fill-color', '#e2e8f0', 'important');
                    inp.style.setProperty('caret-color', '#a78bfa', 'important');
                    inp.style.setProperty('font-size', '13px', 'important');
                    inp.style.setProperty('font-weight', '600', 'important');
                    inp.style.setProperty('background', 'transparent', 'important');
                    inp.style.setProperty('border', 'none', 'important');
                    inp.style.setProperty('letter-spacing', '0.5px', 'important');
                    inp.style.setProperty('flex', '1', 'important');
                    inp.style.setProperty('text-shadow', 'none', 'important');
                }
            }
            inp_wrap.onmouseenter = () => inp_wrap.style.background = 'linear-gradient(135deg,#673DE6,#5353ff,#a78bfa)';
            inp_wrap.onmouseleave = () => inp_wrap.style.background = 'linear-gradient(135deg,rgba(103,61,230,0.6),rgba(83,83,255,0.4),rgba(167,139,250,0.5))';
        });
    }
    setTimeout(styleDateInputs, 500);
    new MutationObserver(styleDateInputs).observe(window.parent.document.body, {childList:true, subtree:true});
    </script>
    """, height=0)

# FILTER DATA
df = df_raw[(df_raw['Timestamp'].dt.date>=d_start) & (df_raw['Timestamp'].dt.date<=d_end)] if not df_raw.empty else df_raw

# --- PAGES ---

if st.session_state.nav_target == "Dashboard Home":
    _now = datetime.now()
    _hour = _now.hour
    _greeting = "Good Morning" if _hour < 12 else "Good Afternoon" if _hour < 17 else "Good Evening"
    _date_str = _now.strftime("%A, %d %B %Y")
    _time_str = _now.strftime("%I:%M %p")
    st.markdown(f"""
<style>
@keyframes welcomeShift {{
  0%   {{ background-position: 0% 50%; }}
  50%  {{ background-position: 100% 50%; }}
  100% {{ background-position: 0% 50%; }}
}}
.welcome-card {{
  width:100%; border-radius:20px;
  display:flex; align-items:center; justify-content:space-between;
  position:relative; overflow:hidden;
  font-family:'Inter','Segoe UI',sans-serif;
  background: linear-gradient(43deg, #0f2027 0%, #203a43 40%, #1a1a2e 100%);
  background-size: 400% 400%;
  animation: welcomeShift 5s ease infinite;
  background-image:
    radial-gradient(at 88% 40%, hsla(220,60%,15%,0.8) 0px, transparent 85%),
    radial-gradient(at 49% 30%, hsla(220,60%,10%,0.7) 0px, transparent 85%),
    radial-gradient(at 14% 26%, hsla(220,60%,10%,0.7) 0px, transparent 85%),
    radial-gradient(at 0%  64%, hsla(263,60%,20%,0.6) 0px, transparent 85%),
    radial-gradient(at 41% 94%, hsla(195,60%,20%,0.5) 0px, transparent 85%),
    radial-gradient(at 100% 99%, hsla(240,60%,20%,0.5) 0px, transparent 85%);
  box-shadow: 0px -16px 24px 0px rgba(255,255,255,0.05) inset,
              0 8px 32px rgba(0,0,0,0.35);
  margin-bottom: 1.4rem;
  padding: 1.6rem 1.6rem;
}}
.welcome-orb {{
  content:""; width:120px; height:120px;
  position:absolute; top:-40%; left:-5%;
  border-radius:50%; border:35px solid rgba(255,255,255,0.18);
  transition:all .8s ease; filter:blur(.5rem);
  pointer-events:none;
}}
</style>
<div class='welcome-card'>
  <div class='welcome-orb'></div>
  <div style='position:relative;z-index:1;'>
    <div style='font-size:10px;color:rgba(255,255,255,0.75);font-weight:600;letter-spacing:1.8px;text-transform:uppercase;margin-bottom:3px;'>{html.escape(_greeting)}</div>
    <div style='font-size:21px;font-weight:800;color:#ffffff;letter-spacing:-0.3px;line-height:1.2;'>Welcome back, <span style='color:#f4e900;text-shadow:0 0 12px rgba(244,233,0,0.4);'>Admin</span> 👋</div>
    <div style='font-size:12px;color:rgba(255,255,255,0.65);font-weight:400;margin-top:4px;'>You have full access to the monitoring suite</div>
  </div>
  <div style='text-align:right;position:relative;z-index:1;'>
    <div style='font-size:20px;font-weight:700;color:#ffffff;letter-spacing:0.5px;'>{html.escape(_time_str)}</div>
    <div style='font-size:12px;color:rgba(255,255,255,0.65);margin-top:2px;'>{html.escape(_date_str)}</div>
    <div style='display:inline-flex;align-items:center;gap:5px;margin-top:7px;background:rgba(247,234,234,0.15);border-radius:20px;padding:3px 12px;font-size:11px;font-weight:600;color:#ffffff;letter-spacing:0.8px;'>
      <span style='width:6px;height:6px;border-radius:50%;background:#f4e900;box-shadow:0 0 6px #f4e900;display:inline-block;'></span> LIVE MONITORING
    </div>
  </div>
</div>
""", unsafe_allow_html=True)
    st.markdown("""
        <div style='margin-bottom:1.6rem;'>
            <div style='font-size:26px; font-weight:700; color:#1D1D2E; letter-spacing:-0.3px;'>🚀 Admin Dashboard</div>
            <div style='font-size:13px; color:#6b7280; font-weight:400; margin-top:4px;'>Real-time employee activity overview</div>
        </div>
    """, unsafe_allow_html=True)
    if not df.empty:
        buffer = datetime.now() - timedelta(minutes=5)
        all_emps = sorted(df['Employee Name'].unique().tolist())
        online_list = df[df['Timestamp'] > buffer]['Employee Name'].unique().tolist()
        offline_list = [e for e in all_emps if e not in online_list]
        is_single_day = (d_start == d_end)
        today_df = df[df['Timestamp'].dt.date == d_start] if is_single_day else df
        login_times = today_df.groupby('Employee Name')['Timestamp'].min().dt.strftime('%I:%M %p').to_dict()
        logout_times = {
            emp: ("--" if emp in online_list else today_df[today_df['Employee Name'] == emp]['Timestamp'].max().strftime('%I:%M %p'))
            for emp in today_df['Employee Name'].unique()
        }

        c1, c2, c3 = st.columns(3)
        with c1:
            # amazonq-ignore-next-line
            if st.button(f" ONLINE\n{len(online_list)}", key="online_btn", use_container_width=True):
                st.session_state.filter_status = "Online"
        with c2:
            # amazonq-ignore-next-line
            if st.button(f" OFFLINE\n{len(offline_list)}", key="offline_btn", use_container_width=True):
                st.session_state.filter_status = "Offline"
        with c3:
            # amazonq-ignore-next-line
            if st.button(f" TOTAL TEAM\n{len(all_emps)}", key="total_btn", use_container_width=True):
                st.session_state.filter_status = "All"

        # JS to style status buttons - animated gradient border
        components.html("""
        <script>
        (function(){
            var style = window.parent.document.getElementById('uv-btn-style');
            if (!style) {
                style = window.parent.document.createElement('style');
                style.id = 'uv-btn-style';
                style.textContent = `
                @keyframes grad-spin { 0%{background-position:0% 50%} 50%{background-position:100% 50%} 100%{background-position:0% 50%} }
                .uv-grad-wrap {
                    padding: 3px !important;
                    border-radius: 25px !important;
                    background-size: 300% 300% !important;
                    animation: grad-spin 3s ease infinite !important;
                    display: block !important;
                    width: 95% !important;
                    margin: 0 auto !important;
                }
                .uv-online-wrap { background-image: linear-gradient(135deg,#10B981,#34D399,#059669,#10B981) !important; }
                .uv-offline-wrap { background-image: linear-gradient(135deg,#e70000,#ff6b6b,#c00000,#e70000) !important; }
                .uv-total-wrap { background-image: linear-gradient(135deg,#3B82F6,#60A5FA,#1D4ED8,#3B82F6) !important; }
                .uv-btn {
                    font-size: 22px !important;
                    font-weight: 800 !important;
                    letter-spacing: 0px !important;
                    text-transform: none !important;
                    background: #fff !important;
                    border: none !important;
                    border-radius: 23px !important;
                    box-shadow: 0px 8px 15px rgba(0,0,0,0.1) !important;
                    transition: all 0.3s ease !important;
                    cursor: pointer !important;
                    outline: none !important;
                    height: 114px !important;
                    width: 100% !important;
                    text-shadow: none !important;
                    line-height: 1.4 !important;
                    white-space: pre-wrap !important;
                }
                .uv-btn p {
                    font-size: 22px !important;
                    font-weight: 800 !important;
                    letter-spacing: 0px !important;
                    text-transform: none !important;
                    line-height: 1.4 !important;
                    text-shadow: none !important;
                    margin: 0 !important;
                }
                .uv-btn:active { transform: translateY(-1px) !important; }
                .uv-online { color: #10B981 !important; }
                .uv-online p { color: #10B981 !important; }
                .uv-online:hover { background: #10B981 !important; box-shadow: 0px 15px 20px rgba(16,185,129,0.4) !important; color: #fff !important; transform: translateY(-7px) !important; }
                .uv-online:hover p { color: #fff !important; }
                .uv-offline { color: #e70000 !important; }
                .uv-offline p { color: #e70000 !important; }
                .uv-offline:hover { background: #e70000 !important; box-shadow: 0px 15px 20px rgba(231,0,0,0.4) !important; color: #fff !important; transform: translateY(-7px) !important; }
                .uv-offline:hover p { color: #fff !important; }
                .uv-total { color: #3B82F6 !important; }
                .uv-total p { color: #3B82F6 !important; }
                .uv-total:hover { background: #3B82F6 !important; box-shadow: 0px 15px 20px rgba(59,130,246,0.4) !important; color: #fff !important; transform: translateY(-7px) !important; }
                .uv-total:hover p { color: #fff !important; }
                `;
                window.parent.document.head.appendChild(style);
            }
            function styleButtons() {
                var btns = window.parent.document.querySelectorAll('button');
                btns.forEach(function(btn) {
                    if (btn.closest('[data-testid="stToolbar"]') || btn.closest('header') || btn.closest('[data-testid="stSidebar"]')) return;
                    var txt = btn.innerText;
                    var isStatus = txt.includes('ONLINE') || txt.includes('OFFLINE') || txt.includes('TOTAL');
                    if (!isStatus || btn.dataset.uvStyled) return;
                    btn.dataset.uvStyled = '1';
                    var isOnline  = txt.includes('ONLINE');
                    var isOffline = txt.includes('OFFLINE');
                    var cls = isOnline ? 'uv-online' : isOffline ? 'uv-offline' : 'uv-total';
                    btn.classList.add('uv-btn', cls);
                    btn.style.setProperty('height', '114px', 'important');
                    btn.style.setProperty('min-height', '114px', 'important');
                    btn.style.setProperty('width', '100%', 'important');
                    btn.style.setProperty('border-radius', '23px', 'important');
                    btn.style.setProperty('border', 'none', 'important');
                    var p = btn.querySelector('p');
                    var textClr = isOnline ? '#10B981' : isOffline ? '#e70000' : '#3B82F6';
                    if (p) {
                        p.style.setProperty('font-size', '22px', 'important');
                        p.style.setProperty('font-weight', '800', 'important');
                        p.style.setProperty('letter-spacing', '0px', 'important');
                        p.style.setProperty('text-transform', 'none', 'important');
                        p.style.setProperty('line-height', '1.4', 'important');
                        p.style.setProperty('color', textClr, 'important');
                        p.style.setProperty('text-shadow', 'none', 'important');
                    }
                    btn.onmouseenter = function() { if (p) p.style.setProperty('color','#ffffff','important'); };
                    btn.onmouseleave = function() { if (p) p.style.setProperty('color', textClr, 'important'); };
                    if (!btn.parentNode.classList.contains('uv-grad-wrap')) {
                        var wrapCls = cls === 'uv-online' ? 'uv-online-wrap' : cls === 'uv-offline' ? 'uv-offline-wrap' : 'uv-total-wrap';
                        var wrap = document.createElement('div');
                        wrap.className = 'uv-grad-wrap ' + wrapCls;
                        btn.parentNode.insertBefore(wrap, btn);
                        wrap.appendChild(btn);
                    }
                });
            }
            setTimeout(styleButtons, 400);
            var obs = new MutationObserver(styleButtons);
            obs.observe(window.parent.document.body, { childList: true, subtree: true });
        })();
        </script>
        """, height=0)

        # JS to apply acrylic glass to main content area
        components.html("""
        <script>
        function styleMain() {
            const main = window.parent.document.querySelector('[data-testid="stAppViewBlockContainer"]') ||
                         window.parent.document.querySelector('.main .block-container') ||
                         window.parent.document.querySelector('[data-testid="block-container"]');
            if (main) {
                main.style.setProperty('background', '#ffffff', 'important');
                main.style.setProperty('border-radius', '20px', 'important');
                main.style.setProperty('box-shadow', '0 4px 24px rgba(15,23,42,0.08)', 'important');
                main.style.setProperty('border', '1px solid #E2E8F0', 'important');
                main.style.setProperty('margin', '0.8rem 0.8rem 0.8rem 0', 'important');
            }
        }
        setTimeout(styleMain, 400);
        </script>
        """, height=0)

        # Section label based on active filter
        if st.session_state.filter_status == "Online":
            components.html("<div style='font-size:14px;font-weight:600;color:#673DE6;background:rgba(103,61,230,0.06);border-left:3px solid rgba(103,61,230,0.4);padding:0.5rem 1rem;border-radius:8px;margin-bottom:0.8rem;border:1px solid rgba(103,61,230,0.12);'>&#127922; Online Employees &nbsp;&middot;&nbsp; <span style='font-weight:400;color:#8b5cf6;'>" + str(len(online_list)) + " members</span></div>", height=50)
        elif st.session_state.filter_status == "Offline":
            components.html("<div style='font-size:14px;font-weight:600;color:#1D1D2E;background:rgba(29,29,46,0.04);border-left:3px solid rgba(29,29,46,0.3);padding:0.5rem 1rem;border-radius:8px;margin-bottom:0.8rem;border:1px solid rgba(29,29,46,0.1);'>&#128308; Offline Employees &nbsp;&middot;&nbsp; <span style='font-weight:400;color:#6b7280;'>" + str(len(offline_list)) + " members</span></div>", height=50)
        else:
            components.html("<div style='font-size:14px;font-weight:600;color:#673DE6;background:rgba(103,61,230,0.06);border-left:3px solid rgba(103,61,230,0.4);padding:0.5rem 1rem;border-radius:8px;margin-bottom:0.8rem;border:1px solid rgba(103,61,230,0.12);'>&#128101; Total Team &nbsp;&middot;&nbsp; <span style='font-weight:400;color:#8b5cf6;'>" + str(len(all_emps)) + " members</span></div>", height=50)

        target = online_list if st.session_state.filter_status=="Online" else offline_list if st.session_state.filter_status=="Offline" else all_emps

        if not target:
            st.markdown("<div style='color:#64748B;font-size:13px;padding:0.4rem 0;'>No employees in this category.</div>", unsafe_allow_html=True)

        # Build Uiverse cards via components.html
        chunk = 5
        for row_start in range(0, max(len(target), 1), chunk):
            row_emps = target[row_start:row_start + chunk]
            if not row_emps: break
            cards_html = ""
            for emp in row_emps:
                is_online = emp in online_list
                login_t  = login_times.get(emp, "--")
                logout_t = logout_times.get(emp, "--")
                dot_color = "#10B981" if is_online else "#94A3B8"
                status_label = "ONLINE" if is_online else "OFFLINE"
                status_color = "#10B981" if is_online else "#F43F5E"
                bg_color = "rgba(16,185,129,0.13)" if is_online else "rgba(105,13,197,0.10)"
                orb_color = "rgba(16,185,129,0.18)" if is_online else "rgba(255,255,255,0.10)"
                safe_emp_js = _js_escape(emp)
                cards_html += f"""
                <div class="uv-card" onclick="empClick('{safe_emp_js}')"
                     style="background:{bg_color};">
                  <div class="uv-orb" style="border-color:{orb_color};"></div>
                  <div class="uv-text">
                    <div class="uv-name">{html.escape(emp)}</div>
                    <div class="uv-status" style="color:{status_color};">
                      <span style="display:inline-block;width:7px;height:7px;border-radius:50%;background:{dot_color};margin-right:5px;{'box-shadow:0 0 6px ' + dot_color if is_online else ''}"></span>
                      {status_label}
                    </div>
                  </div>
                  <div class="uv-footer">
                    <div class="uv-time-block">
                      <span class="uv-time-label">LOGIN</span>
                      <span class="uv-time-val">{html.escape(login_t)}</span>
                    </div>
                    <div class="uv-divider"></div>
                    <div class="uv-time-block">
                      <span class="uv-time-label">LOGOUT</span>
                      <span class="uv-time-val" style="color:{'#10B981' if logout_t == '--' else 'aliceblue'}">{html.escape(logout_t)}</span>
                    </div>
                  </div>
                </div>"""

            components.html(f"""
            <style>
            .uv-grid {{ display:flex; gap:14px; flex-wrap:wrap; padding:4px 0 12px 0; }}
            .uv-card {{
                width:260px; height:190px; border-radius:15px;
                display:flex; flex-direction:column;
                position:relative; overflow:hidden;
                cursor:pointer; transition:transform 0.2s ease, box-shadow 0.2s ease;
                font-family:'Inter','Segoe UI',sans-serif;
                background-image:
                    radial-gradient(at 88% 40%, hsla(240,15%,9%,0.6) 0px, transparent 85%),
                    radial-gradient(at 49% 30%, hsla(240,15%,9%,0.5) 0px, transparent 85%),
                    radial-gradient(at 14% 26%, hsla(240,15%,9%,0.5) 0px, transparent 85%),
                    radial-gradient(at 0%  64%, hsla(263,93%,56%,0.5) 0px, transparent 85%),
                    radial-gradient(at 41% 94%, hsla(284,100%,84%,0.35) 0px, transparent 85%),
                    radial-gradient(at 100% 99%, hsla(306,100%,57%,0.4) 0px, transparent 85%) !important;
                box-shadow: 0px -16px 24px 0px rgba(255,255,255,0.12) inset !important;
            }}
            .uv-card:hover {{ transform:translateY(-4px); box-shadow:0 12px 32px rgba(103,61,230,0.22); }}
            .uv-orb {{
                content:""; width:100px; height:100px;
                position:absolute; top:-40%; left:-20%;
                border-radius:50%; border:35px solid;
                transition:all .8s ease; filter:blur(.5rem);
                pointer-events:none;
            }}
            .uv-card:hover .uv-orb {{
                width:140px; height:140px;
                top:-30%; left:50%;
                filter:blur(0rem);
            }}
            .uv-text {{
                flex-grow:1; padding:14px 14px 6px 14px;
                display:flex; flex-direction:column; gap:6px;
            }}
            .uv-name {{
                color:aliceblue; font-weight:800; font-size:1.1em;
                white-space:nowrap; overflow:hidden; text-overflow:ellipsis;
            }}
            .uv-status {{
                font-size:0.65em; font-weight:600;
                display:flex; align-items:center;
                text-transform:uppercase; letter-spacing:1px;
            }}
            .uv-footer {{
                display:flex; align-items:center; justify-content:space-around;
                background:rgba(247,234,234,0.15);
                border-radius:0 0 15px 15px;
                padding:8px 10px;
                gap:6px;
            }}
            .uv-footer:hover {{ background:rgba(247,234,234,0.25); }}
            .uv-time-block {{ display:flex; flex-direction:column; align-items:center; gap:2px; flex:1; }}
            .uv-time-label {{ font-size:9px; font-weight:600; color:rgba(240,248,255,0.5); letter-spacing:0.8px; }}
            .uv-time-val {{ font-size:11px; font-weight:700; color:aliceblue; white-space:nowrap; }}
            .uv-divider {{ width:1px; height:28px; background:rgba(255,255,255,0.15); }}
            </style>
            <div class="uv-grid">{cards_html}</div>
            <script>
            function empClick(name) {{
                var btns = window.parent.document.querySelectorAll('button');
                btns.forEach(function(b) {{
                    if (b.innerText.trim() === '__emp__' + name) b.click();
                }});
            }}
            </script>
            """, height=220)

            # Hidden Streamlit buttons that trigger navigation
            cols = st.columns(len(row_emps))
            for j, emp in enumerate(row_emps):
                i = row_start + j
                with cols[j]:
                    if st.button(f"__emp__{emp}", key=f"btn_{i}"):
                        st.session_state.selected_emp = emp
                        st.session_state.nav_target = "Employee Insights"
                        st.rerun()
            # Hide the trigger buttons
            components.html("""
            <script>
            (function(){
                function hideEmpBtns() {
                    window.parent.document.querySelectorAll('button').forEach(function(b){
                        if (b.innerText.includes('__emp__')) {
                            b.closest('[data-testid="stButton"]') && (b.closest('[data-testid="stButton"]').style.display = 'none');
                        }
                    });
                }
                setTimeout(hideEmpBtns, 200);
                new MutationObserver(hideEmpBtns).observe(window.parent.document.body, {childList:true, subtree:true});
            })();
            </script>
            """, height=0)

elif st.session_state.nav_target == "Employee Insights":
    if st.button("← Back", key="back_insights", type="secondary"):
        st.session_state.nav_target = "Dashboard Home"
        st.rerun()
    # Uiverse back button style
    components.html("""
    <script>
    (function(){
        function styleBack() {
            var btns = window.parent.document.querySelectorAll('button');
            btns.forEach(function(btn) {
                if (btn.dataset.backStyled) return;
                var txt = btn.innerText.trim();
                if (txt !== '← Back') return;
                btn.dataset.backStyled = '1';
                
                // Base button
                btn.style.setProperty('background', '#ffffff', 'important');
                btn.style.setProperty('border', '3px solid #ffffff', 'important');
                btn.style.setProperty('border-radius', '12px', 'important');
                btn.style.setProperty('height', '42px', 'important');
                btn.style.setProperty('min-height', '42px', 'important');
                btn.style.setProperty('width', '110px', 'important');
                btn.style.setProperty('position', 'relative', 'important');
                btn.style.setProperty('overflow', 'hidden', 'important');
                btn.style.setProperty('box-shadow', '0 2px 8px rgba(0,0,0,0.08)', 'important');
                btn.style.setProperty('transition', 'none', 'important');
                btn.style.setProperty('display', 'flex', 'important');
                btn.style.setProperty('align-items', 'center', 'important');
                btn.style.setProperty('justify-content', 'center', 'important');
                
                // Clear inner content
                btn.innerHTML = '';
                
                // Purple expanding div with arrow
                var purpleDiv = document.createElement('div');
                purpleDiv.style.cssText = 'position:absolute;left:0;top:0;background:#673DE6;border-radius:9px;height:36px;width:30%;display:flex;align-items:center;justify-content:center;z-index:1;transition:width 0.5s ease;';
                purpleDiv.innerHTML = `<svg width="18px" height="18px" viewBox="0 0 1024 1024" xmlns="http://www.w3.org/2000/svg"><path fill="#ffffff" d="M224 480h640a32 32 0 1 1 0 64H224a32 32 0 0 1 0-64z"></path><path fill="#ffffff" d="m237.248 512 265.408 265.344a32 32 0 0 1-45.312 45.312l-288-288a32 32 0 0 1 0-45.312l288-288a32 32 0 1 1 45.312 45.312L237.248 512z"></path></svg>`;
                btn.appendChild(purpleDiv);
                
                // Text — anchored to right so expanding purple never covers it
                var textP = document.createElement('p');
                textP.innerText = 'Back';
                textP.style.cssText = 'position:absolute;right:12px;z-index:99;color:#000000;font-size:13px;font-weight:600;margin:0;pointer-events:none;transition:color 0.4s ease;white-space:nowrap;';
                btn.appendChild(textP);
                
                // Hover
                btn.onmouseenter = function() {
                    purpleDiv.style.width = '100%';
                    textP.style.color = '#ffffff';
                };
                btn.onmouseleave = function() {
                    purpleDiv.style.width = '30%';
                    textP.style.color = '#000000';
                };
            });
        }
        setTimeout(styleBack, 300);
        new MutationObserver(styleBack).observe(window.parent.document.body, {childList:true, subtree:true});
    })();
    </script>
    """, height=0)
    st.markdown("""
        <div style='margin-bottom:1.6rem;'>
            <div style='font-size:26px; font-weight:700; color:#1D1D2E; letter-spacing:-0.3px;'>👤 Performance Profile</div>
            <div style='font-size:13px; color:#6b7280; font-weight:400; margin-top:4px;'>Individual employee activity breakdown</div>
        </div>
    """, unsafe_allow_html=True)
    if not df.empty:
        all_emps = sorted(df['Employee Name'].unique().tolist())
        sel_idx = all_emps.index(st.session_state.selected_emp) if st.session_state.selected_emp in all_emps else 0
        selected = st.selectbox("Select Team Member", all_emps, index=sel_idx)
        m_df = df[df['Employee Name'] == selected]
        t_u = m_df[m_df['Type'] == "Working"]['Duration'].sum()
        i_u = m_df[m_df['Type'] == "Idle"]['Duration'].sum()

        is_single_day = (d_start == d_end)
        emp_day = m_df[m_df['Timestamp'].dt.date == d_start] if is_single_day else m_df
        buffer_check = datetime.now() - timedelta(minutes=5)
        is_online = not emp_day.empty and emp_day['Timestamp'].max() > buffer_check
        login_time_str = emp_day['Timestamp'].min().strftime('%I:%M %p') if not emp_day.empty else "--"
        logout_time_str = "--" if (emp_day.empty or is_online) else emp_day['Timestamp'].max().strftime('%I:%M %p')

        col1, col2, col3, col4 = st.columns(4)
        logout_color = '#673DE6' if logout_time_str == '--' else '#1D1D2E'
        col1.markdown(
            "<div style='background:#ffffff;border:1px solid rgba(103,61,230,0.15);border-radius:12px;padding:1rem 1.2rem;box-shadow:0 2px 8px rgba(103,61,230,0.08);height:100%;'>"
            "<div style='color:#673DE6;font-size:11px;font-weight:600;text-transform:uppercase;letter-spacing:0.8px;margin-bottom:8px;'>&#128336; Session Time</div>"
            "<div style='display:flex;align-items:center;gap:8px;'>"
            "<div><div style='font-size:10px;color:#6b7280;font-weight:500;margin-bottom:2px;'>Login</div>"
            "<div style='font-size:17px;font-weight:600;color:#1D1D2E;'>" + html.escape(login_time_str) + "</div></div>"
            "<div style='color:#d1d5db;font-size:16px;padding:0 2px;'>&#8594;</div>"
            "<div><div style='font-size:10px;color:#6b7280;font-weight:500;margin-bottom:2px;'>Logout</div>"
            "<div style='font-size:17px;font-weight:600;color:" + html.escape(logout_color) + ";'>" + html.escape(logout_time_str) + "</div></div>"
            "</div></div>",
            unsafe_allow_html=True
        )
        col2.metric("Work Time", format_time(t_u))
        col3.metric("Idle Time", format_time(i_u))
        col4.metric("Efficiency", f"{int((t_u/(t_u+i_u))*100)}%" if (t_u+i_u)>0 else "0%")

        summary_df = pd.DataFrame({'Status':['Work','Idle'], 'Minutes':[t_u, i_u], 'Time':[format_time(t_u), format_time(i_u)]})
        fig_bar = go.Figure([
            go.Bar(
                x=summary_df['Status'], y=summary_df['Minutes'],
                text=summary_df['Time'], textposition='inside',
                textfont=dict(size=15, color='#ffffff', family='Inter'),
                marker=dict(
                    color=['#2d6a4f','#bc4749'],
                    line=dict(width=0),
                    cornerradius=8
                ),
                width=0.4,
                hovertemplate='<b>%{x}</b><br>%{text}<extra></extra>'
            )
        ])
        fig_bar.update_layout(
            paper_bgcolor='#ffffff', plot_bgcolor='#f4f3ff',
            margin=dict(l=20, r=20, t=10, b=20), height=340,
            font=dict(family='Inter', color='#1D1D2E', size=13),
            showlegend=False,
            xaxis=dict(showgrid=False, zeroline=True, zerolinecolor='rgba(103,61,230,0.15)', zerolinewidth=1, tickfont=dict(size=13, color='#6b7280', family='Inter'), linecolor='rgba(103,61,230,0.15)', linewidth=1),
            yaxis=dict(showgrid=True, gridcolor='rgba(103,61,230,0.08)', gridwidth=1, zeroline=True, zerolinecolor='rgba(103,61,230,0.15)', zerolinewidth=1, rangemode='tozero', tickfont=dict(size=12, color='#6b7280'), title=dict(text='Minutes', font=dict(size=12, color='#9ca3af')), linecolor='rgba(103,61,230,0.15)', linewidth=1),
            bargap=0.4
        )
        st.plotly_chart(fig_bar, use_container_width=True)

        cl1, cl2 = st.columns(2)
        with cl1:
            st.markdown("<div style='font-size:16px;font-weight:600;color:#1D1D2E;margin-bottom:0.5rem;'>💻 Software Logs</div>", unsafe_allow_html=True)
            apps = m_df[m_df['Category']=="Application"].groupby('Clean Name')['Duration'].sum().reset_index()
            apps['Time'] = apps['Duration'].apply(format_time)
            st.dataframe(apps[['Clean Name','Time']], use_container_width=True, hide_index=True)
        with cl2:
            st.markdown("<div style='font-size:16px;font-weight:600;color:#1D1D2E;margin-bottom:0.5rem;'>🌐 Website Logs</div>", unsafe_allow_html=True)
            webs = m_df[m_df['Category']=="Website"].groupby('Clean Name')['Duration'].sum().reset_index()
            webs['Time'] = webs['Duration'].apply(format_time)
            st.dataframe(webs[['Clean Name','Time']], use_container_width=True, hide_index=True)

elif st.session_state.nav_target == "Screenshots":
    import base64
    SCREENSHOT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Screenshots")
    if st.button("← Back", key="back_shots", type="secondary"):
        st.session_state.nav_target = "Dashboard Home"
        st.rerun()
    # Uiverse back button style
    components.html("""
    <script>
    (function(){
        function styleBack() {
            var btns = window.parent.document.querySelectorAll('button');
            btns.forEach(function(btn) {
                if (btn.dataset.backStyled) return;
                var txt = btn.innerText.trim();
                if (txt !== '← Back') return;
                btn.dataset.backStyled = '1';
                
                // Base button
                btn.style.setProperty('background', '#ffffff', 'important');
                btn.style.setProperty('border', '3px solid #ffffff', 'important');
                btn.style.setProperty('border-radius', '12px', 'important');
                btn.style.setProperty('height', '42px', 'important');
                btn.style.setProperty('min-height', '42px', 'important');
                btn.style.setProperty('width', '110px', 'important');
                btn.style.setProperty('position', 'relative', 'important');
                btn.style.setProperty('overflow', 'hidden', 'important');
                btn.style.setProperty('box-shadow', '0 2px 8px rgba(0,0,0,0.08)', 'important');
                btn.style.setProperty('transition', 'none', 'important');
                btn.style.setProperty('display', 'flex', 'important');
                btn.style.setProperty('align-items', 'center', 'important');
                btn.style.setProperty('justify-content', 'center', 'important');
                
                // Clear inner content
                btn.innerHTML = '';
                
                // Purple expanding div with arrow
                var purpleDiv = document.createElement('div');
                purpleDiv.style.cssText = 'position:absolute;left:0;top:0;background:#673DE6;border-radius:9px;height:36px;width:30%;display:flex;align-items:center;justify-content:center;z-index:1;transition:width 0.5s ease;';
                purpleDiv.innerHTML = `<svg width="18px" height="18px" viewBox="0 0 1024 1024" xmlns="http://www.w3.org/2000/svg"><path fill="#ffffff" d="M224 480h640a32 32 0 1 1 0 64H224a32 32 0 0 1 0-64z"></path><path fill="#ffffff" d="m237.248 512 265.408 265.344a32 32 0 0 1-45.312 45.312l-288-288a32 32 0 0 1 0-45.312l288-288a32 32 0 1 1 45.312 45.312L237.248 512z"></path></svg>`;
                btn.appendChild(purpleDiv);
                
                // Text — anchored to right so expanding purple never covers it
                var textP = document.createElement('p');
                textP.innerText = 'Back';
                textP.style.cssText = 'position:absolute;right:12px;z-index:99;color:#000000;font-size:13px;font-weight:600;margin:0;pointer-events:none;transition:color 0.4s ease;white-space:nowrap;';
                btn.appendChild(textP);
                
                // Hover
                btn.onmouseenter = function() {
                    purpleDiv.style.width = '100%';
                    textP.style.color = '#ffffff';
                };
                btn.onmouseleave = function() {
                    purpleDiv.style.width = '30%';
                    textP.style.color = '#000000';
                };
            });
        }
        setTimeout(styleBack, 300);
        new MutationObserver(styleBack).observe(window.parent.document.body, {childList:true, subtree:true});
    })();
    </script>
    """, height=0)
    st.markdown("""
        <div style='margin-bottom:1.6rem;'>
            <div style='font-size:26px;font-weight:700;color:#1D1D2E;letter-spacing:-0.3px;'>📸 Screenshots</div>
            <div style='font-size:13px;color:#6b7280;font-weight:400;margin-top:4px;'>Employee screen captures — every 2 hours</div>
        </div>
    """, unsafe_allow_html=True)
    if not os.path.exists(SCREENSHOT_DIR) or not os.listdir(SCREENSHOT_DIR):
        st.markdown("<div style='color:#6b7280;font-size:14px;padding:2rem;text-align:center;background:#f4f3ff;border:1px solid rgba(103,61,230,0.15);border-radius:12px;'>No screenshots yet. They will appear here once the collector runs.</div>", unsafe_allow_html=True)
    else:
        files = sorted([f for f in os.listdir(SCREENSHOT_DIR) if f.endswith('.png')], reverse=True)
        emp_shots = {}
        for f in files:
            parts = f.replace('.png','').split('_')
            emp = parts[0] if parts else 'Unknown'
            # Filter by date range — filename format: EmpName_YYYY-MM-DD_HH-MM.png
            try:
                file_date = datetime.fromisoformat(parts[1]).date()
                if not (d_start <= file_date <= d_end):
                    continue
            except (IndexError, ValueError) as e:
                logging.error("Failed to parse screenshot date for %s: %s", f, e)
            emp_shots.setdefault(emp, []).append(f)
        all_shot_emps = sorted(emp_shots.keys())
        if not all_shot_emps:
            st.markdown("<div style='color:#6b7280;font-size:14px;padding:2rem;text-align:center;background:#f4f3ff;border:1px solid rgba(103,61,230,0.15);border-radius:12px;'>No screenshots found for the selected date range.</div>", unsafe_allow_html=True)
        else:
            sel_emp = st.selectbox("Filter by Employee", ["All"] + all_shot_emps)
            show_emps = all_shot_emps if sel_emp == "All" else [sel_emp]

            # Build full HTML grid with lightbox — rendered via components.html so JS works
            cards_html = ""
            total_height = 0
            for emp in show_emps:
                shots = emp_shots[emp][:20]
                cards_html += f"<div style='font-size:15px;font-weight:700;color:#1D1D2E;margin:1.2rem 0 0.6rem 0;border-left:3px solid #673DE6;padding-left:10px;'>{html.escape(emp)}</div>"
                cards_html += "<div style='display:grid;grid-template-columns:repeat(4,1fr);gap:12px;margin-bottom:1rem;'>"
                for fname in shots:
                    fpath = os.path.join(SCREENSHOT_DIR, fname)
                    try:
                        with open(fpath, 'rb') as f:
                            b64 = base64.b64encode(f.read()).decode()
                        parts = fname.replace('.png','').split('_')
                        ts = ' '.join(parts[-2:]).replace('-', '/') if len(parts) >= 2 else fname
                        src = "data:image/png;base64," + b64
                        cards_html += (
                            f"<div onclick=\"openLB('{src}','{ts.replace(chr(39), '')}')\" "
                            "style='border:1px solid rgba(103,61,230,0.15);border-radius:10px;overflow:hidden;"
                            "box-shadow:0 2px 8px rgba(103,61,230,0.08);cursor:zoom-in;transition:transform 0.18s;'"
                            " onmouseover=\"this.style.transform='scale(1.03)'\" onmouseout=\"this.style.transform='scale(1)'\">"
                            f"<img src='{src}' style='width:100%;height:180px;object-fit:cover;display:block;'/>"
                            f"<div style='padding:6px 10px;font-size:11px;color:#6b7280;font-weight:500;background:#f4f3ff;'>{html.escape(ts)}</div>"
                            "</div>"
                        )
                        total_height += 240
                    except Exception as e:
                        logging.error("Failed to load screenshot %s: %s", fname, e)
                cards_html += "</div>"

            components.html(f"""
        <!-- Lightbox -->
        <div id='lb' style='display:none;position:fixed;inset:0;z-index:99999;
            background:rgba(0,0,0,0.92);align-items:center;justify-content:center;flex-direction:column;'>

            <!-- Toolbar -->
            <div style='position:fixed;top:16px;right:20px;display:flex;align-items:center;gap:10px;z-index:100000;'>
                <button onclick="zoom(-0.2)" title="Zoom Out"
                    style='width:38px;height:38px;border-radius:50%;border:none;background:rgba(255,255,255,0.12);
                    color:#fff;font-size:20px;cursor:pointer;display:flex;align-items:center;justify-content:center;
                    backdrop-filter:blur(6px);transition:background 0.2s;'
                    onmouseover="this.style.background='rgba(255,255,255,0.25)'"
                    onmouseout="this.style.background='rgba(255,255,255,0.12)'">&#8722;</button>
                <span id='zoom-label' style='color:#94A3B8;font-size:13px;font-weight:600;min-width:42px;text-align:center;'>100%</span>
                <button onclick="zoom(0.2)" title="Zoom In"
                    style='width:38px;height:38px;border-radius:50%;border:none;background:rgba(255,255,255,0.12);
                    color:#fff;font-size:20px;cursor:pointer;display:flex;align-items:center;justify-content:center;
                    backdrop-filter:blur(6px);transition:background 0.2s;'
                    onmouseover="this.style.background='rgba(255,255,255,0.25)'"
                    onmouseout="this.style.background='rgba(255,255,255,0.12)'">&#43;</button>
                <button onclick="resetZoom()" title="Reset"
                    style='height:38px;padding:0 14px;border-radius:20px;border:none;background:rgba(255,255,255,0.12);
                    color:#fff;font-size:12px;font-weight:600;cursor:pointer;letter-spacing:0.5px;
                    backdrop-filter:blur(6px);transition:background 0.2s;'
                    onmouseover="this.style.background='rgba(255,255,255,0.25)'"
                    onmouseout="this.style.background='rgba(255,255,255,0.12)'">RESET</button>
                <button onclick="closeLB()" title="Close"
                    style='width:38px;height:38px;border-radius:50%;border:none;background:rgba(220,38,38,0.7);
                    color:#fff;font-size:18px;cursor:pointer;display:flex;align-items:center;justify-content:center;
                    backdrop-filter:blur(6px);transition:background 0.2s;'
                    onmouseover="this.style.background='rgba(220,38,38,1)'"
                    onmouseout="this.style.background='rgba(220,38,38,0.7)'">&#10005;</button>
            </div>

            <!-- Image wrapper (scrollable/pannable) -->
            <div id='lb-wrap' style='overflow:auto;width:100vw;height:100vh;display:flex;
                align-items:center;justify-content:center;'>
                <img id='lb-img' src='' style='border-radius:8px;box-shadow:0 8px 48px rgba(0,0,0,0.7);
                    transform-origin:center center;transition:transform 0.2s ease;cursor:grab;
                    max-width:none;'/>
            </div>

            <!-- Caption -->
            <div id='lb-cap' style='position:fixed;bottom:18px;left:50%;transform:translateX(-50%);
                color:#94A3B8;font-size:13px;font-weight:500;background:rgba(0,0,0,0.5);
                padding:6px 18px;border-radius:20px;backdrop-filter:blur(6px);white-space:nowrap;'></div>
        </div>

        {cards_html}

        <script>
        var _scale = 1;
        var _dragging = false, _startX, _startY, _scrollLeft, _scrollTop;

        function openLB(src, cap) {{
            _scale = 1;
            var img = document.getElementById('lb-img');
            img.src = src;
            img.style.transform = 'scale(1)';
            img.style.width = 'auto';
            img.style.maxWidth = '95vw';
            img.style.maxHeight = '90vh';
            img.style.height = 'auto';
            document.getElementById('lb-cap').innerText = cap;
            document.getElementById('zoom-label').innerText = '100%';
            document.getElementById('lb').style.display = 'flex';
        }}
        function closeLB() {{ document.getElementById('lb').style.display = 'none'; }}
        function zoom(delta) {{
            _scale = Math.min(Math.max(_scale + delta, 0.2), 5);
            document.getElementById('lb-img').style.transform = 'scale(' + _scale + ')';
            document.getElementById('zoom-label').innerText = Math.round(_scale * 100) + '%';
        }}
        function resetZoom() {{
            _scale = 1;
            var img = document.getElementById('lb-img');
            img.style.transform = 'scale(1)';
            img.style.width = 'auto';
            img.style.maxWidth = '95vw';
            img.style.maxHeight = '90vh';
            document.getElementById('zoom-label').innerText = '100%';
        }}

        // Mouse wheel zoom
        document.getElementById('lb-wrap').addEventListener('wheel', function(e) {{
            if (document.getElementById('lb').style.display === 'none') return;
            e.preventDefault();
            zoom(e.deltaY < 0 ? 0.15 : -0.15);
        }}, {{ passive: false }});

        // Drag to pan
        var wrap = document.getElementById('lb-wrap');
        wrap.addEventListener('mousedown', function(e) {{
            _dragging = true;
            _startX = e.pageX - wrap.offsetLeft;
            _startY = e.pageY - wrap.offsetTop;
            _scrollLeft = wrap.scrollLeft;
            _scrollTop = wrap.scrollTop;
            wrap.style.cursor = 'grabbing';
        }});
        wrap.addEventListener('mouseleave', function() {{ _dragging = false; wrap.style.cursor = 'grab'; }});
        wrap.addEventListener('mouseup',    function() {{ _dragging = false; wrap.style.cursor = 'grab'; }});
        wrap.addEventListener('mousemove',  function(e) {{
            if (!_dragging) return;
            e.preventDefault();
            wrap.scrollLeft = _scrollLeft - (e.pageX - wrap.offsetLeft - _startX);
            wrap.scrollTop  = _scrollTop  - (e.pageY - wrap.offsetTop  - _startY);
        }});

        // ESC to close
        document.addEventListener('keydown', function(e) {{ if (e.key === 'Escape') closeLB(); }});
        </script>
            """, height=max(total_height, 600), scrolling=True)

elif st.session_state.nav_target == "App Analytics":
    st.markdown("""
        <div style='margin-bottom:1.6rem;'>
            <div style='font-size:26px; font-weight:700; color:#1D1D2E; letter-spacing:-0.3px;'>&#128269; Resource Intelligence</div>
            <div style='font-size:13px; color:#6b7280; font-weight:400; margin-top:4px;'>Application and website usage analytics</div>
        </div>
    """, unsafe_allow_html=True)
    if not df.empty:
        app_data = df.groupby('Clean Name')['Duration'].sum().reset_index()
        clist, ctabs = st.columns([1, 2.5])
        with clist:
            st.markdown("<div style='font-size:16px;font-weight:600;color:#1D1D2E;margin-bottom:0.5rem;'>🔧 Toggle Apps</div>", unsafe_allow_html=True)
            st.markdown("<style>.stCheckbox label p, .stCheckbox label span { color: #1D1D2E !important; text-shadow: none !important; font-weight: 500 !important; } .stCheckbox { background: #f4f3ff !important; border-radius: 8px !important; padding: 4px 10px !important; margin-bottom: 3px !important; border: 1px solid rgba(103,61,230,0.15) !important; }</style>", unsafe_allow_html=True)
            selected_apps = [r['Clean Name'] for _,r in app_data.iterrows() if st.checkbox(r['Clean Name'], value=True)]
        with ctabs:
            t1, t2 = st.tabs(["Pie Distribution", "User Breakdown"])
            with t1:
                if selected_apps:
                    pie_df = app_data[app_data['Clean Name'].isin(selected_apps)]
                    n = len(pie_df)
                    _palette = (px.colors.qualitative.Set2 + px.colors.qualitative.Pastel + px.colors.qualitative.Vivid)
                    _colors = (_palette * ((n // len(_palette)) + 1))[:n]
                    fig_pie = go.Figure(go.Pie(
                        labels=pie_df['Clean Name'], values=pie_df['Duration'],
                        hole=0.48,
                        pull=[0.03]*n,
                        textposition='inside',
                        textinfo='percent+label',
                        textfont=dict(size=12, family='Inter'),
                        marker=dict(
                            colors=_colors,
                            line=dict(color='#ffffff', width=2)
                        ),
                        rotation=45,
                        hovertemplate='<b>%{label}</b><br>%{percent}<extra></extra>'
                    ))
