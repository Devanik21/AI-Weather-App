import streamlit as st
import google.generativeai as genai
from datetime import datetime, timedelta

st.set_page_config(
    page_title="AI Weather Assistant",
    page_icon="🌤️",
    layout="wide"
)

# Inject some CSS for color magic ✨
st.markdown("""
    <style>
    .main-title {
        background: linear-gradient(90deg, #fceabb, #f8b500);
        padding: 1rem;
        border-radius: 12px;
        text-align: center;
        color: white;
        font-size: 2.5rem;
        font-weight: bold;
        margin-bottom: 20px;
    }

    .emoji-card {
        background-color: #fff6f6;
        border-radius: 20px;
        padding: 1rem;
        box-shadow: 2px 2px 8px rgba(0,0,0,0.1);
        text-align: center;
    }

    .response-card {
        background-color: #f9f9ff;
        padding: 1.5rem;
        border-radius: 15px;
        border-left: 5px solid #a0c4ff;
        box-shadow: 2px 2px 8px rgba(0,0,0,0.05);
        font-size: 1.05rem;
    }
    </style>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.title("🌤️ AI Weather")
    api_key = st.text_input("Enter Gemini API Key", type="password")
    st.caption("Your API key is kept private and not stored")

    location = st.text_input("Enter location", placeholder="New York, Paris, Tokyo...")
    time_frame = st.selectbox(
        "Select time frame",
        ["Current weather", "Today's forecast", "Weekly forecast"]
    )
    show_details = st.checkbox("Show detailed information", value=True)
    submit = st.button("Get Weather Info")

# Title
st.markdown("<div class='main-title'>🌤️ AI Weather Assistant</div>", unsafe_allow_html=True)

if not api_key:
    st.info("Please enter your Gemini API key in the sidebar to start.")
elif not location:
    st.info("Enter a location in the sidebar to get weather information.")
elif submit:
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel(model_name="gemini-2.0-flash")

        with st.spinner("Fetching weather information... ☁️"):
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
                st.caption("Weather visualization")

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
st.caption("✨ Powered by Google's Gemini 2.0 Flash | Styled with love 💛")
