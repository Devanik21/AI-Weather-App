import streamlit as st
import google.generativeai as genai
from datetime import datetime, timedelta

st.set_page_config(
    page_title="AI Weather Assistant",
    page_icon="🌙",
    layout="wide"
)

# Custom CSS for dark mode styling
st.markdown("""
    <style>
    .main-title {
        background: linear-gradient(90deg, #0f2027, #203a43, #2c5364);
        padding: 1rem;
        border-radius: 12px;
        text-align: center;
        color: #ffffff;
        font-size: 2.5rem;
        font-weight: bold;
        margin-bottom: 20px;
        box-shadow: 0px 0px 15px #00ffe0;
    }

    .emoji-card {
        background-color: transparent;
        padding: 1rem;
        text-align: center;
    }

    .response-card {
        padding: 1.2rem;
        border-left: 4px solid #00ffe0;
        border-radius: 8px;
        font-size: 1.05rem;
        color: #e0e0e0;
        background-color: rgba(0, 0, 0, 0.3);
    }

    .stTextInput > div > div > input {
        color: white !important;
    }

    .stTextInput > div > label {
        color: #ccc !important;
    }
    </style>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.title("🌙 AI Weather (Dark)")
    api_key = st.text_input("Enter Gemini API Key", type="password")
    st.caption("Your API key is kept private and not stored")

    location = st.text_input("Enter location", placeholder="Tokyo, Berlin, etc.")
    time_frame = st.selectbox(
        "Select time frame",
        ["Current weather", "Today's forecast", "Weekly forecast"]
    )
    show_details = st.checkbox("Show detailed information", value=True)
    submit = st.button("Get Weather Info")

# Main Title
st.markdown("<div class='main-title'>🌙 AI Weather Assistant</div>", unsafe_allow_html=True)

if not api_key:
    st.info("Please enter your Gemini API key in the sidebar to start.")
elif not location:
    st.info("Enter a location in the sidebar to get weather information.")
elif submit:
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel(model_name="gemini-2.0-flash")

        with st.spinner("Retrieving weather data... 🌌"):
            now = datetime.now()
            today_str = now.strftime("%A, %d %B %Y")

            if time_frame == "Current weather":
                date_info = f"as of now ({today_str})"
            elif time_frame == "Today's forecast":
                date_info = f"for today ({today_str})"
            elif time_frame == "Weekly forecast":
                week_dates = [(now + timedelta(days=i)).strftime("%A, %d %B") for i in range(7)]
                date_info = f"for the upcoming week ({', '.join(week_dates)})"

            detail_level = "detailed" if show_details else "brief"

            prompt = f"""
Act as a professional weather forecaster.
Provide {detail_level} weather information for **{location}**, {date_info}.

If detailed information is requested, include:
- Temperature (actual and feels like)
- Humidity and precipitation chances
- Wind speed and direction
- Air quality
- Sunrise and sunset times
- Any weather alerts or warnings

Use clear formatting (like bullet points). If unsure about data, state it's an estimate.
Also provide 1–2 friendly weather tips (e.g., carry an umbrella or stay hydrated).
"""

            response = model.generate_content(prompt)

            st.subheader(f"📍 {location} — {time_frame}")
            st.markdown(f"<div class='response-card'>{response.text}</div>", unsafe_allow_html=True)

            col1, col2 = st.columns([3, 1])
            with col2:
                st.markdown("<div class='emoji-card'>", unsafe_allow_html=True)
                st.caption("Weather visual")

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

                st.markdown(f"<h1 style='font-size: 6rem'>{weather_emoji}</h1>", unsafe_allow_html=True)
                st.markdown("</div>", unsafe_allow_html=True)

    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
        if "403" in str(e) or "401" in str(e):
            st.error("API key error. Please check your Gemini API key.")
        elif "429" in str(e):
            st.error("Rate limit exceeded. Please try again later.")

# Footer
st.markdown("---")
st.caption("✨ Powered by Gemini 2.0 Flash | Dark Mode Activated 🌌")
