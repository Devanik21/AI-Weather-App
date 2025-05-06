import streamlit as st
import google.generativeai as genai
from datetime import datetime, timedelta
import ephem
import math

st.set_page_config(
    page_title="Cyberpunk AI Weather",
    page_icon="🌌",
    layout="wide"
)

# --- Accurate Moon Phase Calculation ---
def get_moon_phase(date: datetime):
    moon = ephem.Moon()
    observer = ephem.Observer()
    observer.date = date
    moon.compute(observer)
    phase = moon.phase  # 0 to ~29.53

    if phase < 1.5:
        return "🌑 New"
    elif phase < 6.7:
        return "🌒 Waxing Crescent"
    elif phase < 13.8:
        return "🌓 First Quarter"
    elif phase < 20.7:
        return "🌔 Waxing Gibbous"
    elif phase < 23.8:
        return "🌕 Full"
    elif phase < 27.0:
        return "🌖 Waning Gibbous"
    elif phase < 29.0:
        return "🌗 Last Quarter"
    else:
        return "🌘 Waning Crescent"

# --- Cyberpunk CSS ---
st.markdown("""
    <style>
    body {
        background-color: #000000;
    }
    .main-title {
        background: linear-gradient(90deg, #ff0080, #7928ca);
        padding: 1rem;
        border-radius: 14px;
        text-align: center;
        color: white;
        font-size: 2.5rem;
        font-weight: bold;
        margin-bottom: 20px;
        box-shadow: 0px 0px 20px #ff00cc;
        letter-spacing: 1.5px;
    }
    .emoji-card {
        text-align: center;
        animation: pulse 2s infinite;
    }
    .response-card {
        padding: 1.3rem;
        border-left: 4px solid #ff00cc;
        border-radius: 8px;
        font-size: 1.05rem;
        color: #e0e0e0;
        background-color: rgba(20, 20, 20, 0.5);
    }
    .moon {
        font-size: 1.2rem;
        color: #8affff;
        padding-top: 10px;
    }
    @keyframes pulse {
        0% { transform: scale(1); }
        50% { transform: scale(1.08); }
        100% { transform: scale(1); }
    }
    .stTextInput > div > div > input {
        color: white !important;
    }
    .stTextInput > div > label {
        color: #ccc !important;
    }
    </style>
""", unsafe_allow_html=True)

# --- Sidebar ---
with st.sidebar:
    st.title("🌌 Cyberpunk Weather")
    api_key = st.text_input("Enter Gemini API Key", type="password")
    st.caption("🔐 We never store your key")

    location = st.text_input("📍 Enter location", placeholder="Neo-Tokyo, Night City...")
    time_frame = st.selectbox("🕒 Select time frame", ["Current weather", "Today's forecast", "Weekly forecast"])
    show_details = st.checkbox("🌠 Show detailed info", value=True)
    submit = st.button("⚡ Get Weather")

# --- Title ---
st.markdown("<div class='main-title'>🌌 Cyberpunk AI Weather Assistant</div>", unsafe_allow_html=True)

# --- Weather Logic ---
if not api_key:
    st.info("Please enter your Gemini API key in the sidebar.")
elif not location:
    st.info("Enter a location to get started.")
elif submit:
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel(model_name="gemini-2.0-flash")

        with st.spinner("🌐 Fetching weather intel..."):
            now = datetime.now()
            today_str = now.strftime("%A, %d %B %Y")

            if time_frame == "Current weather":
                date_info = f"as of now ({today_str})"
            elif time_frame == "Today's forecast":
                date_info = f"for today ({today_str})"
            elif time_frame == "Weekly forecast":
                week_dates = [(now + timedelta(days=i)).strftime("%a, %b %d") for i in range(7)]
                date_info = f"for the upcoming week: {', '.join(week_dates)}"

            detail_level = "detailed" if show_details else "brief"

            prompt = f"""
Act as a professional weather forecaster in a cyberpunk world.
Provide {detail_level} weather info for **{location}**, {date_info}.

If detailed:
- Temperature (actual and feels like)
- Humidity, rain chance
- Wind speed & direction
- Air quality index (AQI)
- Sunrise/sunset times
- Alerts or warnings

Add 1–2 helpful tips like: “Pack an umbrella” or “Wear sunscreen.”
"""

            response = model.generate_content(prompt)

            st.subheader(f"📡 {location} — {time_frame}")
            st.markdown(f"<div class='response-card'>{response.text}</div>", unsafe_allow_html=True)

            # Emoji & Moon Phase
            col1, col2 = st.columns([3, 1])
            with col2:
                weather_emoji = "🌤️"
                text = response.text.lower()
                if "rain" in text:
                    weather_emoji = "🌧️"
                elif "cloud" in text:
                    weather_emoji = "☁️"
                elif "sunny" in text or "clear" in text:
                    weather_emoji = "☀️"
                elif "snow" in text:
                    weather_emoji = "❄️"
                elif "storm" in text or "thunder" in text:
                    weather_emoji = "⛈️"

                moon = get_moon_phase(datetime.now())
                st.markdown(f"<div class='emoji-card'><h1 style='font-size: 6rem;'>{weather_emoji}</h1></div>", unsafe_allow_html=True)
                st.markdown(f"<div class='moon'>🌙 Moon phase: {moon}</div>", unsafe_allow_html=True)

    except Exception as e:
        st.error(f"Oops: {str(e)}")
        if "403" in str(e) or "401" in str(e):
            st.error("API key error. Double-check your key.")
        elif "429" in str(e):
            st.error("Too many requests. Try again soon.")

# --- Footer ---
st.markdown("---")
st.caption("⚡ Powered by Gemini Flash | Accurate Moon Phase by PyEphem 🌕")
