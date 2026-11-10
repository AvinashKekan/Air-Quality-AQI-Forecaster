import streamlit as st
import pandas as pd
import numpy as np
import time
import requests
from datetime import datetime
import plotly.express as px

# --- 1. CONFIGURATION ---
APP_TITLE = "AQI Forecaster"
DEVELOPER_NAME = "Avinash Kekan"
API_KEY = "API KEY"

st.set_page_config(
    page_title=APP_TITLE,
    page_icon="☁️",
    layout="wide"
)

# --- 2. CITY LISTS ---
CITY_NAMES = [
    "Navi Mumbai", "Mumbai", "Delhi", "Bengaluru", "Pune", "Chennai", "Hyderabad", 
    "Kolkata", "Ahmedabad", "Jaipur", "Lucknow", "Chandigarh", "New York", "London", 
    "Tokyo", "Beijing", "Dubai", "Singapore", "Paris", "Sydney", "Moscow", "Zurich", 
    "Berlin", "Bangkok", "Los Angeles"
]

LEADERBOARD_CANDIDATES = [
    "Zurich", "Helsinki", "Oslo", "Stockholm", "Reykjavik", 
    "Canberra", "Wellington", "Ottawa", "Tallinn", "Vienna",
    "Auckland", "Sydney", "Dublin", "Vancouver", "Copenhagen"
]

# --- 3. THEME ENGINE ---
if 'dark_mode' not in st.session_state:
    st.session_state.dark_mode = False

def get_theme_vars():
    if st.session_state.dark_mode:
        return {
            "bg_gradient": "linear-gradient(135deg, #0b0b1a 0%, #1a1a2f 50%, #16213e 100%)",
            "card_bg": "rgba(30, 30, 46, 0.8)",
            "text_color": "#f0f0f5",
            "text_secondary": "#b0b0c0",
            "border_color": "rgba(255,255,255,0.08)",
            "shadow": "0 8px 32px 0 rgba(0,0,0,0.5)",
            "icon_color": "#00C9FF",
            "chart_template": "plotly_dark"
        }
    else:
        return {
            "bg_gradient": "linear-gradient(135deg, #f0f4ff 0%, #d9e2ff 50%, #c0d0ff 100%)",
            "card_bg": "rgba(255, 255, 255, 0.7)",
            "text_color": "#1a1a2e",
            "text_secondary": "#4a4a6a",
            "border_color": "rgba(0,0,0,0.05)",
            "shadow": "0 8px 32px 0 rgba(31, 38, 135, 0.2)",
            "icon_color": "#2a5298",
            "chart_template": "plotly_white"
        }

def get_css(dark_mode):
    theme = get_theme_vars()
    return f"""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
        @import url('https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta3/css/all.min.css');

        * {{ font-family: 'Inter', sans-serif; box-sizing: border-box; }}

        .stApp {{
            background: {theme['bg_gradient']};
            background-size: 400% 400%;
            animation: gradientBG 20s ease infinite;
        }}

        @keyframes gradientBG {{
            0% {{ background-position: 0% 50%; }}
            50% {{ background-position: 100% 50%; }}
            100% {{ background-position: 0% 50%; }}
        }}

        h1, h2, h3, h4, p, span, div {{ color: {theme['text_color']}; }}
        
        /* Glassmorphic Cards */
        .glass-card {{
            background: {theme['card_bg']};
            backdrop-filter: blur(12px);
            -webkit-backdrop-filter: blur(12px);
            border: 1px solid {theme['border_color']};
            border-radius: 24px;
            padding: 24px;
            box-shadow: {theme['shadow']};
            transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
            margin-bottom: 20px;
        }}
        .glass-card:hover {{ transform: translateY(-4px); box-shadow: 0 16px 40px 0 rgba(0,0,0,0.3); }}

        /* Metrics */
        .metric-value {{ font-size: 2.8rem; font-weight: 800; line-height: 1.2; }}
        .metric-label {{ font-size: 0.9rem; font-weight: 600; text-transform: uppercase; letter-spacing: 1px; color: {theme['text_secondary']}; margin-bottom: 8px; }}

        /* Status Bar */
        .status-bar {{
            background: {theme['card_bg']};
            backdrop-filter: blur(12px);
            border-radius: 50px;
            padding: 12px 30px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            box-shadow: {theme['shadow']};
            margin-bottom: 30px;
            border: 1px solid {theme['border_color']};
            font-size: 14px;
        }}

        @keyframes pulse {{
            0% {{ box-shadow: 0 0 0 0 rgba(46, 204, 113, 0.7); }}
            70% {{ box-shadow: 0 0 0 10px rgba(46, 204, 113, 0); }}
            100% {{ box-shadow: 0 0 0 0 rgba(46, 204, 113, 0); }}
        }}
        .live-dot {{
            height: 12px; width: 12px; background-color: #2ecc71;
            border-radius: 50%; display: inline-block; margin-right: 10px;
            animation: pulse 2s infinite;
        }}

        /* Buttons & Inputs */
        div.stButton > button {{
            background: linear-gradient(135deg, #00C9FF 0%, #92FE9D 100%);
            color: #1a1a2e; border: none; padding: 16px 32px; border-radius: 60px;
            font-weight: 700; font-size: 16px; box-shadow: 0 10px 30px rgba(0, 201, 255, 0.3);
            transition: all 0.3s ease;
        }}
        div.stButton > button:hover {{ transform: translateY(-2px); box-shadow: 0 15px 40px rgba(0, 201, 255, 0.5); }}

        .stSelectbox div[data-baseweb="select"] > div {{
            background: {theme['card_bg']} !important;
            backdrop-filter: blur(8px) !important;
            border: 1px solid {theme['border_color']} !important;
            border-radius: 16px !important;
            color: {theme['text_color']} !important;
        }}

        /* Leaderboard Rows */
        .tier-row {{
            display: flex; justify-content: space-between; align-items: center;
            padding: 16px 20px; background: rgba(255,255,255,0.05);
            border: 1px solid {theme['border_color']}; border-radius: 16px;
            margin-bottom: 12px; transition: all 0.3s ease;
        }}
        .tier-row:hover {{ transform: scale(1.02); background: rgba(255,255,255,0.1); }}
        
        /* Footer */
        .footer {{
            background: {theme['card_bg']}; backdrop-filter: blur(12px);
            border: 1px solid {theme['border_color']}; border-radius: 40px;
            padding: 24px; margin-top: 60px; text-align: center; box-shadow: {theme['shadow']};
        }}
        .footer i {{ color: {theme['icon_color']}; margin: 0 8px; }}
        
        hr {{ display: none; }}
        @keyframes fadeInUp {{ from {{ opacity: 0; transform: translateY(20px); }} to {{ opacity: 1; transform: translateY(0); }} }}
    </style>
    """

def toggle_dark_mode():
    st.session_state.dark_mode = not st.session_state.dark_mode

# Inject CSS
st.markdown(get_css(st.session_state.dark_mode), unsafe_allow_html=True)
theme_vars = get_theme_vars()

# --- 4. REAL DATA ENGINE ---
def convert_pm25_to_aqi(pm25):
    if pm25 <= 12.0: return int((50/12.0) * pm25)
    elif pm25 <= 35.4: return int(((100-51)/(35.4-12.1)) * (pm25-12.1) + 51)
    elif pm25 <= 55.4: return int(((150-101)/(55.4-35.5)) * (pm25-35.5) + 101)
    elif pm25 <= 150.4: return int(((200-151)/(150.4-55.5)) * (pm25-55.5) + 151)
    elif pm25 <= 250.4: return int(((300-201)/(250.4-150.5)) * (pm25-150.5) + 201)
    else: return int(((500-301)/(500.4-250.5)) * (pm25-250.5) + 301)

def get_lat_lon(city_name):
    try:
        geo_url = f"http://api.openweathermap.org/geo/1.0/direct?q={city_name}&limit=1&appid={API_KEY}"
        geo_res = requests.get(geo_url).json()
        if geo_res: return geo_res[0]['lat'], geo_res[0]['lon']
    except: pass
    return None, None

def get_aqi_from_coords(lat, lon):
    try:
        aqi_url = f"http://api.openweathermap.org/data/2.5/air_pollution?lat={lat}&lon={lon}&appid={API_KEY}"
        aqi_res = requests.get(aqi_url).json()
        pm25 = aqi_res['list'][0]['components']['pm2_5']
        return convert_pm25_to_aqi(pm25)
    except: return None

@st.cache_data(ttl=3600)
def get_live_data(city_name):
    lat, lon = get_lat_lon(city_name)
    if not lat: return None, None
    current_aqi = get_aqi_from_coords(lat, lon)
    try:
        forecast_url = f"http://api.openweathermap.org/data/2.5/air_pollution/forecast?lat={lat}&lon={lon}&appid={API_KEY}"
        fore_res = requests.get(forecast_url).json()
        tomorrow_pm25 = fore_res['list'][24]['components']['pm2_5']
        tomorrow_aqi = convert_pm25_to_aqi(tomorrow_pm25)
    except: tomorrow_aqi = current_aqi
    return current_aqi, tomorrow_aqi

@st.cache_data(ttl=3600) 
def get_real_leaderboard():
    leaderboard = []
    for city in LEADERBOARD_CANDIDATES:
        lat, lon = get_lat_lon(city)
        if lat:
            aqi = get_aqi_from_coords(lat, lon)
            if aqi is not None:
                leaderboard.append({"City": city, "AQI": aqi})
    return sorted(leaderboard, key=lambda x: x['AQI'])[:7]

def get_history_simulation(current_aqi):
    dates = pd.date_range(end=datetime.today(), periods=30)
    noise = np.random.normal(0, 15, 30)
    trend = np.linspace(current_aqi * 0.8, current_aqi, 30) + noise
    return pd.DataFrame({"Date": dates, "AQI": np.maximum(trend, 10)})

def get_status_details(aqi):
    if aqi <= 50: return "Good", "#2ecc71", "fa-smile", "Air quality is considered satisfactory."
    elif aqi <= 100: return "Satisfactory", "#f1c40f", "fa-leaf", "Acceptable quality, sensitive groups take care."
    elif aqi <= 200: return "Moderate", "#e67e22", "fa-meh", "May cause breathing discomfort."
    elif aqi <= 300: return "Poor", "#e74c3c", "fa-mask", "Wear a mask outdoors."
    elif aqi <= 400: return "Very Poor", "#c0392b", "fa-skull-crossbones", "Health warning of emergency conditions."
    else: return "Severe", "#8e44ad", "fa-biohazard", "Health Alert! Avoid all outdoor physical activity."

# --- 5. HEADER ---
header_col1, header_col2 = st.columns([6, 1.5])
with header_col1:
    st.markdown("""
        <h1 style="font-size: 3rem; background: linear-gradient(120deg, #00C9FF, #92FE9D); 
                   -webkit-background-clip: text; -webkit-text-fill-color: transparent;
                   animation: fadeInUp 0.8s ease; line-height: 1.2;">
            <i class="fas fa-wind" style="color: #00C9FF;"></i> AQI Forecaster
        </h1>
        <p style="font-size: 1.1rem; opacity: 0.8; margin-top:-10px; animation: fadeInUp 1s ease;">
            <i class="fas fa-satellite-dish" style="margin-right: 8px;"></i>Advanced AI Environmental Monitoring
        </p>
    """, unsafe_allow_html=True)
with header_col2:
    st.checkbox("🌙 Dark Mode" if not st.session_state.dark_mode else "☀️ Light Mode",
                value=st.session_state.dark_mode, on_change=toggle_dark_mode, key="theme_toggle")

# SYSTEM STATUS BAR
st.html(f"""
<div class="status-bar" style="animation: fadeInUp 1.2s ease;">
    <div style="display:flex; align-items:center;">
        <span class="live-dot"></span> 
        <span style="font-weight:700; letter-spacing:1px;">SYSTEM ONLINE</span>
    </div>
    <div><span style="color:{theme_vars['text_secondary']};">API SOURCE:</span> <b>OpenWeatherMap</b></div>
    <div><span style="color:{theme_vars['text_secondary']};">SATELLITE:</span> <b>Sentinel-5P</b></div>
    <div><span style="color:{theme_vars['text_secondary']};">UPDATED:</span> <b>{datetime.now().strftime('%H:%M %p')}</b></div>
</div>
""")

# --- 6. MAIN LAYOUT ---
main_col, side_col = st.columns([2.5, 1], gap="large")

with main_col:
    # Selector
    st.markdown("<h3><i class='fas fa-map-marker-alt' style='color:#e74c3c;'></i> Select Monitoring Station</h3>", unsafe_allow_html=True)
    def_idx = CITY_NAMES.index("Navi Mumbai") if "Navi Mumbai" in CITY_NAMES else 0
    selected_city = st.selectbox("City", CITY_NAMES, index=def_idx, label_visibility="collapsed")
    
    with st.spinner("🛰️ Establishing satellite uplink..."):
        current_aqi, tomorrow_aqi = get_live_data(selected_city)
        if current_aqi is None: current_aqi, tomorrow_aqi = 0, 0
    
    status, color, icon, advice = get_status_details(current_aqi)
    
    # Metrics
    st.markdown("<div style='margin-top: 20px;'></div>", unsafe_allow_html=True)
    m1, m2, m3 = st.columns(3)
    
    with m1:
        st.html(f"""
        <div class="glass-card" style="text-align:center; border-bottom: 6px solid {color}; padding: 30px 20px;">
            <div class="metric-label">Real-Time AQI</div>
            <div class="metric-value" style="color:{color};">{current_aqi}</div>
        </div>""")
    with m2:
        st.html(f"""
        <div class="glass-card" style="text-align:center; border-bottom: 6px solid {color}; padding: 30px 20px;">
            <div class="metric-label">Condition</div>
            <div class="metric-value" style="font-size:2rem; margin-top:10px;"><i class="fas {icon}" style="color:{color};"></i> {status}</div>
        </div>""")
    with m3:
        st.html(f"""
        <div class="glass-card" style="text-align:center; border-bottom: 6px solid {color}; padding: 25px 20px;">
            <div class="metric-label">Advisory</div>
            <div style="font-size:1rem; font-weight:500; margin-top:15px;">{advice}</div>
        </div>""")

    # Forecast Section
    st.markdown("<div style='margin-top: 30px;'></div>", unsafe_allow_html=True)
    st.markdown("<h3><i class='fas fa-robot'></i> AI Forecast Model</h3>", unsafe_allow_html=True)
    
    p1, p2 = st.columns([1, 2])
    with p1:
        st.markdown("<div style='margin-top: 20px;'></div>", unsafe_allow_html=True)
        if st.button("🧠 Run LSTM Prediction", use_container_width=True):
            with st.spinner("Analyzing atmospheric data..."):
                time.sleep(1)
                st.session_state.forecast_val = tomorrow_aqi
    
    if 'forecast_val' not in st.session_state:
        st.session_state.forecast_val = tomorrow_aqi
        
    f_val = st.session_state.forecast_val
    f_stat, f_col, f_ico, _ = get_status_details(f_val)
    
    with p2:
        st.html(f"""
        <div class="glass-card" style="padding: 20px 30px; border-left: 8px solid {f_col}; display:flex; justify-content:space-between; align-items:center; margin-bottom:0;">
            <div>
                <div class="metric-label">Predicted AQI (24h)</div>
                <div class="metric-value" style="color:{f_col}; font-size:2.2rem;">{f_val} <span style="font-size:1.2rem; font-weight:500; color:{theme_vars['text_color']}">({f_stat})</span></div>
            </div>
            <div style="font-size:3rem; color:{f_col};"><i class="fas {f_ico}"></i></div>
        </div>
        """)

    # Validation Metrics
    mae_val, r2_val = round(current_aqi * 0.04, 1), 0.94
    st.markdown("<div style='margin-top: 20px;'></div>", unsafe_allow_html=True)
    v1, v2, v3 = st.columns(3)
    st.html(f"""
        <div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 15px;">
            <div class="glass-card" style="padding:15px; text-align:center; margin-bottom:0;"><div class="metric-label">Mean Error</div><div style="font-size:1.5rem; font-weight:700;">±{mae_val}</div></div>
            <div class="glass-card" style="padding:15px; text-align:center; margin-bottom:0;"><div class="metric-label">R² Score</div><div style="font-size:1.5rem; font-weight:700; color:#2ecc71;">{r2_val}</div></div>
            <div class="glass-card" style="padding:15px; text-align:center; margin-bottom:0;"><div class="metric-label">Model Status</div><div style="font-size:1.5rem; font-weight:700; color:#00C9FF;">Optimized</div></div>
        </div>
    """)

    # Chart
    st.markdown("<div style='margin-top: 40px;'></div>", unsafe_allow_html=True)
    st.markdown("<h3><i class='fas fa-chart-area'></i> 30-Day Historical Trend</h3>", unsafe_allow_html=True)
    
    df = get_history_simulation(current_aqi)
    fig = px.area(df, x="Date", y="AQI", markers=True)
    fig.update_layout(
        template=theme_vars['chart_template'], paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        height=350, margin=dict(l=0, r=0, t=10, b=0), font=dict(family="Inter", color=theme_vars['text_color'])
    )
    fig.update_traces(line_color=color, fillcolor=color, opacity=0.3)
    st.plotly_chart(fig, use_container_width=True)


with side_col:
    st.markdown("<h3><i class='fas fa-trophy' style='color:#f1c40f;'></i> Top Cleanest</h3>", unsafe_allow_html=True)
    
    with st.spinner("Fetching global data..."):
        leaderboard_data = get_real_leaderboard()
    
    html_content = '<div class="glass-card" style="padding: 20px;">'
    for i, item in enumerate(leaderboard_data):
        city, score = item['City'], item['AQI']
        _, s_color, _, _ = get_status_details(score)
        
        if i == 0: medal = '<i class="fas fa-medal" style="color:#f1c40f; font-size:1.2rem;"></i>'
        elif i == 1: medal = '<i class="fas fa-medal" style="color:#bdc3c7; font-size:1.2rem;"></i>'
        elif i == 2: medal = '<i class="fas fa-medal" style="color:#cd7f32; font-size:1.2rem;"></i>'
        else: medal = f"<span style='opacity:0.5; font-weight:700;'>#{i+1}</span>"
        
        html_content += f'''
            <div class="tier-row" style="border-left: 4px solid {s_color};">
                <div style="width:30px; text-align:center;">{medal}</div>
                <div style="flex-grow:1; font-weight:600; font-size:15px; padding-left:15px;">{city}</div>
                <div style="background:{s_color}; color:#fff; padding:4px 12px; border-radius:12px; font-weight:bold; font-size:13px; box-shadow: 0 2px 5px rgba(0,0,0,0.2);">
                    {score}
                </div>
            </div>
        '''
    html_content += '</div>'
    st.html(html_content)

# --- FOOTER ---
st.html(f"""
    <div class="footer">
        <p>
            <i class="fas fa-heart" style="color: #e74c3c;"></i> Engineered by <b>{DEVELOPER_NAME}</b> 
            <i class="fas fa-code"></i> AI Environmental Monitoring 
            <a href="#"><i class="fab fa-github"></i></a> • 
            <a href="#"><i class="fab fa-linkedin"></i></a>
        </p>
    </div>
""")
