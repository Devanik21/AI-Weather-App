import streamlit as st
import google.generativeai as genai
from datetime import datetime, timedelta
import plotly.graph_objects as go
import pandas as pd
import random
import folium
from streamlit_folium import folium_static
from geopy.geocoders import Nominatim
import requests
import pycountry
import base64
from io import BytesIO
from PIL import Image
import time

st.set_page_config(
    page_title="AI Weather Assistant Pro",
    page_icon="🌙",
    layout="wide"
)

# Enhanced CSS with animations and improved styling
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
        animation: glow 2s ease-in-out infinite alternate;
    }

    @keyframes glow {
        from {
            box-shadow: 0 0 5px #00ffe0, 0 0 10px #00ffe0;
        }
        to {
            box-shadow: 0 0 10px #00ffe0, 0 0 20px #00ffe0, 0 0 30px #00ffe0;
        }
    }

    .emoji-card {
        background-color: transparent;
        padding: 1rem;
        text-align: center;
        transition: transform 0.3s ease;
    }
    
    .emoji-card:hover {
        transform: scale(1.05);
    }

    .response-card {
        padding: 1.2rem;
        border-left: 4px solid #00ffe0;
        border-radius: 8px;
        font-size: 1.05rem;
        color: #e0e0e0;
        background-color: rgba(0, 0, 0, 0.3);
        transition: all 0.3s ease;
    }
    
    .response-card:hover {
        box-shadow: 0 0 15px rgba(0, 255, 224, 0.5);
    }

    .stTextInput > div > div > input {
        color: white !important;
    }

    .stTextInput > div > label {
        color: #ccc !important;
    }
    
    .feature-card {
        background: rgba(44, 62, 80, 0.8);
        border-radius: 10px;
        padding: 15px;
        margin-bottom: 15px;
        border-left: 3px solid #00ffe0;
        transition: all 0.3s ease;
    }
    
    .feature-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 5px 15px rgba(0, 255, 224, 0.2);
    }
    
    .theme-selector {
        background: rgba(30, 30, 30, 0.7);
        padding: 10px;
        border-radius: 8px;
        margin-bottom: 15px;
    }
    
    .loading-animation {
        width: 100%;
        text-align: center;
        font-size: 24px;
        color: #00ffe0;
        animation: bounce 1s infinite;
    }
    
    @keyframes bounce {
        0%, 100% { transform: translateY(0); }
        50% { transform: translateY(-10px); }
    }
    
    .compare-table {
        background: rgba(20, 20, 20, 0.6);
        border-radius: 8px;
        padding: 10px;
    }
    
    .notification {
        position: fixed;
        bottom: 20px;
        right: 20px;
        background: rgba(0, 0, 0, 0.8);
        color: white;
        padding: 10px 20px;
        border-radius: 5px;
        border-left: 4px solid #00ffe0;
        z-index: 9999;
        animation: slideIn 0.5s forwards;
    }
    
    @keyframes slideIn {
        from { transform: translateX(100%); }
        to { transform: translateX(0); }
    }
    
    /* Custom tabs styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    
    .stTabs [data-baseweb="tab"] {
        background-color: rgba(30, 30, 30, 0.7);
        border-radius: 6px 6px 0px 0px;
        padding: 10px 20px;
        border: none;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: rgba(0, 255, 224, 0.2) !important;
        border-bottom: 2px solid #00ffe0 !important;
    }
    </style>
""", unsafe_allow_html=True)

# FEATURE 1: User Profiles & Settings Manager
if 'user_profiles' not in st.session_state:
    st.session_state.user_profiles = {
        "default": {
            "name": "User",
            "favorite_locations": ["Tokyo", "New York", "London"],
            "preferred_units": "metric",
            "theme": "dark",
            "notifications": True
        }
    }
    st.session_state.current_profile = "default"

if 'api_key_saved' not in st.session_state:
    st.session_state.api_key_saved = False

if 'show_notification' not in st.session_state:
    st.session_state.show_notification = False
    st.session_state.notification_message = ""

if 'chart_data' not in st.session_state:
    # Mock data for temperature forecast (will be replaced with real data)
    dates = [(datetime.now() + timedelta(days=i)).strftime("%a") for i in range(7)]
    st.session_state.chart_data = {
        "dates": dates,
        "temps": [random.randint(60, 85) for _ in range(7)],
        "precip": [random.randint(0, 100) for _ in range(7)]
    }

if 'language' not in st.session_state:
    st.session_state.language = "English"

if 'theme_color' not in st.session_state:
    st.session_state.theme_color = "#00ffe0"

# Helper Functions
def show_notification(message):
    st.session_state.show_notification = True
    st.session_state.notification_message = message

def get_coordinates(location):
    try:
        geolocator = Nominatim(user_agent="weather_app")
        loc = geolocator.geocode(location)
        if loc:
            return loc.latitude, loc.longitude
        return None, None
    except:
        return None, None

def get_random_weather_fact():
    facts = [
        "Lightning strikes the Earth about 8.6 million times per day.",
        "A hurricane can release energy equivalent to 10,000 nuclear bombs.",
        "The fastest recorded wind speed on Earth is 253 mph, during a tropical cyclone in Australia.",
        "Snow isn't actually white! Snow crystals are actually translucent.",
        "The air around a lightning bolt can heat up to 50,000°F — five times hotter than the sun's surface!",
        "Raindrops aren't tear-shaped. They're actually shaped more like tiny hamburger buns.",
        "A single snowstorm can drop 39 million tons of snow.",
        "The coldest temperature ever recorded on Earth was -128.6°F in Antarctica.",
        "Wind doesn't make a sound until it blows against an object.",
        "Clouds can weigh more than a million pounds."
    ]
    return random.choice(facts)

def get_mock_historical_data(location):
    # In a real app, you would fetch this from an API
    months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    avg_temps = [random.randint(50, 90) for _ in range(12)]
    avg_precip = [random.randint(0, 100) for _ in range(12)]
    
    return {
        "months": months,
        "avg_temps": avg_temps,
        "avg_precip": avg_precip
    }

def get_mock_air_quality(location):
    # In a real app, this would come from an air quality API
    aqi = random.randint(30, 150)
    pollutants = {
        "PM2.5": random.randint(5, 50),
        "PM10": random.randint(15, 70),
        "O3": random.randint(20, 120),
        "NO2": random.randint(10, 80),
        "SO2": random.randint(5, 40),
        "CO": random.randint(1, 15)
    }
    
    if aqi < 50:
        status = "Good"
        color = "green"
    elif aqi < 100:
        status = "Moderate"
        color = "yellow"
    elif aqi < 150:
        status = "Unhealthy for Sensitive Groups"
        color = "orange"
    else:
        status = "Unhealthy"
        color = "red"
        
    return {
        "aqi": aqi,
        "status": status,
        "color": color,
        "pollutants": pollutants
    }

def compare_locations(locations):
    # Create mock comparative data
    comparison_data = {}
    for loc in locations:
        comparison_data[loc] = {
            "temp": f"{random.randint(60, 90)}°F",
            "humidity": f"{random.randint(30, 95)}%",
            "wind": f"{random.randint(0, 30)} mph",
            "precip": f"{random.randint(0, 100)}%"
        }
    return comparison_data

def translate_weather_phrase(phrase, target_language):
    # Mock translation function - in a real app, you'd use a translation API
    translations = {
        "Sunny": {
            "Spanish": "Soleado",
            "French": "Ensoleillé",
            "Japanese": "晴れ",
            "German": "Sonnig"
        },
        "Cloudy": {
            "Spanish": "Nublado",
            "French": "Nuageux",
            "Japanese": "曇り",
            "German": "Bewölkt"
        },
        "Rainy": {
            "Spanish": "Lluvioso",
            "French": "Pluvieux",
            "Japanese": "雨",
            "German": "Regnerisch"
        }
    }
    
    if phrase in translations and target_language in translations[phrase]:
        return translations[phrase][target_language]
    return phrase

# FEATURE 2: Animated Weather Map
def create_weather_map(location):
    lat, lon = get_coordinates(location)
    if not lat or not lon:
        lat, lon = 35.6762, 139.6503  # Default to Tokyo if location not found
    
    m = folium.Map(location=[lat, lon], zoom_start=10, tiles="CartoDB dark_matter")
    
    # Add marker for the location
    folium.Marker(
        [lat, lon],
        popup=f"<i>{location}</i>",
        tooltip=location,
        icon=folium.Icon(color="blue", icon="cloud")
    ).add_to(m)
    
    # Add a circle to represent weather intensity
    folium.Circle(
        radius=random.randint(5000, 20000),
        location=[lat, lon],
        popup="Weather System",
        color="#00ffe0",
        fill=True,
        fill_opacity=0.2
    ).add_to(m)
    
    # Add nearby cities (simulated)
    for i in range(3):
        offset_lat = random.uniform(-0.5, 0.5)
        offset_lon = random.uniform(-0.5, 0.5)
        folium.Marker(
            [lat + offset_lat, lon + offset_lon],
            popup=f"Nearby Area {i+1}",
            icon=folium.Icon(color="green", icon="info-sign")
        ).add_to(m)
    
    return m

# Sidebar Navigation
with st.sidebar:
    tabs = st.radio("Navigation", ["Weather", "Settings", "Compare", "Historical Data"])
    
    if tabs == "Weather":
        st.title("🌙 AI Weather Pro")
        
        # FEATURE 3: API Key Management & Memory
        if not st.session_state.api_key_saved:
            api_key = st.text_input("Enter Gemini API Key", type="password")
            save_key = st.checkbox("Remember this API key")
            if save_key and api_key:
                st.session_state.api_key = api_key
                st.session_state.api_key_saved = True
                show_notification("API key saved successfully!")
        else:
            st.success("API key is saved ✓")
            if st.button("Clear saved API key"):
                st.session_state.api_key_saved = False
                st.session_state.api_key = ""
                st.experimental_rerun()
        
        # FEATURE 4: Enhanced Location Selector with Favorites
        profile = st.session_state.user_profiles[st.session_state.current_profile]
        location_options = [""] + profile["favorite_locations"] + ["Custom"]
        location_choice = st.selectbox("Select location", location_options)
        
        if location_choice == "Custom":
            location = st.text_input("Enter location", placeholder="Tokyo, Berlin, etc.")
            if location and location not in profile["favorite_locations"]:
                if st.button("Add to favorites"):
                    profile["favorite_locations"].append(location)
                    show_notification(f"Added {location} to favorites!")
        elif location_choice:
            location = location_choice
        else:
            location = ""
        
        # Time frame selector with more options
        time_frame = st.selectbox(
            "Select time frame",
            ["Current weather", "Today's forecast", "24-hour forecast", "3-day forecast", "Weekly forecast"]
        )
        
        show_details = st.checkbox("Show detailed information", value=True)
        
        # FEATURE 5: Units Toggle
        units = st.radio("Units", ["Metric (°C)", "Imperial (°F)"], 
                        index=0 if profile["preferred_units"] == "metric" else 1)
        profile["preferred_units"] = "metric" if units.startswith("Metric") else "imperial"
        
        # FEATURE 6: Language Selection
        languages = ["English", "Spanish", "French", "Japanese", "German"]
        st.session_state.language = st.selectbox("Language", languages)
        
        # Submit button with animation
        submit = st.button("Get Weather Info", use_container_width=True)
        
    elif tabs == "Settings":
        st.title("⚙️ Settings")
        
        # User profile settings
        profile = st.session_state.user_profiles[st.session_state.current_profile]
        profile["name"] = st.text_input("Your Name", value=profile["name"])
        
        # FEATURE 7: Theme Customization
        st.subheader("Theme Settings")
        theme_options = {
            "#00ffe0": "Cyber Teal",
            "#ff5e78": "Neon Pink",
            "#a566ff": "Purple Haze",
            "#00ff9d": "Matrix Green",
            "#ffcc00": "Golden Sun"
        }
        selected_theme = st.selectbox("Theme Color", list(theme_options.values()))
        for color, name in theme_options.items():
            if name == selected_theme:
                st.session_state.theme_color = color
        
        st.markdown(f"<div style='background-color:{st.session_state.theme_color}; height:20px; border-radius:10px;'></div>", unsafe_allow_html=True)
        
        # Notification settings
        profile["notifications"] = st.checkbox("Enable notifications", value=profile["notifications"])
        
        # Clear data option
        if st.button("Reset All Settings"):
            # Reset to defaults
            for key in st.session_state.keys():
                del st.session_state[key]
            st.experimental_rerun()
    
    elif tabs == "Compare":
        st.title("🔍 Compare Locations")
        
        # FEATURE 8: Location Comparison
        st.subheader("Select locations to compare")
        
        # Get all user's favorite locations
        all_locations = st.session_state.user_profiles[st.session_state.current_profile]["favorite_locations"]
        
        # Allow selecting up to 3 locations to compare
        selected_locations = []
        for i in range(1, 4):
            loc = st.selectbox(f"Location {i}", [""] + all_locations, key=f"compare_{i}")
            if loc:
                selected_locations.append(loc)
        
        compare_button = st.button("Compare Weather", use_container_width=True)
    
    elif tabs == "Historical Data":
        st.title("📊 Historical Weather")
        
        # Location for historical data
        location_hist = st.selectbox(
            "Select location",
            [""] + st.session_state.user_profiles[st.session_state.current_profile]["favorite_locations"],
            key="hist_location"
        )
        
        # Year selection
        year = st.selectbox("Select year", list(range(datetime.now().year, datetime.now().year-10, -1)))
        
        view_historical = st.button("View Historical Data", use_container_width=True)

# Weather Fact of the Day
if random.random() < 0.7:  # 70% chance to show weather fact
    with st.expander("🔍 Weather Fact of the Day", expanded=False):
        st.info(get_random_weather_fact())

# Main Content Area
if tabs == "Weather":
    # Main Title with theme color
    st.markdown(f"<div class='main-title' style='box-shadow: 0px 0px 15px {st.session_state.theme_color};'>🌙 AI Weather Assistant Pro</div>", unsafe_allow_html=True)
    
    if not st.session_state.api_key_saved and not 'api_key' in st.session_state:
        st.info("Please enter your Gemini API key in the sidebar to start.")
    elif not location:
        st.info("Select or enter a location in the sidebar to get weather information.")
    elif submit:
        try:
            # Get API key from session state or sidebar input
            api_key = st.session_state.api_key if st.session_state.api_key_saved else api_key
            
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel(model_name="gemini-2.0-flash")
            
            # Loading animation
            with st.spinner(""):
                st.markdown("<div class='loading-animation'>Retrieving weather data...</div>", unsafe_allow_html=True)
                
                # Simulate loading for better UX
                progress_bar = st.progress(0)
                for i in range(100):
                    time.sleep(0.01)
                    progress_bar.progress(i + 1)
                st.empty()
                
                now = datetime.now()
                today_str = now.strftime("%A, %d %B %Y")
                
                if time_frame == "Current weather":
                    date_info = f"as of now ({today_str})"
                elif time_frame == "Today's forecast":
                    date_info = f"for today ({today_str})"
                elif time_frame == "24-hour forecast":
                    date_info = f"for the next 24 hours (starting {today_str})"
                elif time_frame == "3-day forecast":
                    three_days = [(now + timedelta(days=i)).strftime("%A, %d %B") for i in range(3)]
                    date_info = f"for the next 3 days ({', '.join(three_days)})"
                elif time_frame == "Weekly forecast":
                    week_dates = [(now + timedelta(days=i)).strftime("%A, %d %B") for i in range(7)]
                    date_info = f"for the upcoming week ({', '.join(week_dates)})"
                
                detail_level = "detailed" if show_details else "brief"
                units_text = "Celsius" if units.startswith("Metric") else "Fahrenheit"
                
                prompt = f"""
Act as a professional weather forecaster.
Provide {detail_level} weather information for **{location}**, {date_info}.
Use {units_text} for temperature measurements.

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
                
                # FEATURE 9: Weather Visualization System
                # Create tabs for different views
                tab1, tab2, tab3, tab4 = st.tabs(["Forecast", "Map", "Charts", "Air Quality"])
                
                with tab1:
                    st.subheader(f"📍 {location} — {time_frame}")
                    
                    # Display the AI response
                    st.markdown(f"<div class='response-card'>{response.text}</div>", unsafe_allow_html=True)
                    
                    # Weather emoji display
                    col1, col2 = st.columns([3, 1])
                    with col2:
                        st.markdown("<div class='emoji-card'>", unsafe_allow_html=True)
                        st.caption("Weather visual")
                        
                        # Choose weather emoji based on keywords in response
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
                        elif "fog" in text or "mist" in text:
                            weather_emoji = "🌫️"
                        
                        st.markdown(f"<h1 style='font-size: 6rem'>{weather_emoji}</h1>", unsafe_allow_html=True)
                        st.markdown("</div>", unsafe_allow_html=True)
                        
                        # FEATURE 10: Language Translation
                        if st.session_state.language != "English":
                            st.markdown("---")
                            st.markdown("#### Translation")
                            # Simulate translation for key weather terms
                            if "sunny" in text:
                                translated = translate_weather_phrase("Sunny", st.session_state.language)
                                st.write(f"Sunny → {translated}")
                            elif "cloudy" in text:
                                translated = translate_weather_phrase("Cloudy", st.session_state.language)
                                st.write(f"Cloudy → {translated}")
                            elif "rain" in text:
                                translated = translate_weather_phrase("Rainy", st.session_state.language)
                                st.write(f"Rainy → {translated}")
                    
                with tab2:
                    st.subheader(f"Weather Map: {location}")
                    
                    # Create and display weather map
                    map_data = create_weather_map(location)
                    folium_static(map_data, width=800)
                    
                    st.caption("Map shows approximate weather systems and nearby areas")
                
                with tab3:
                    st.subheader("Weather Forecast Charts")
                    
                    # Generate mock forecast data for the chart based on response text
                    mock_temps = []
                    for i in range(7):
                        base_temp = random.randint(65, 85)
                        if "cold" in text.lower() or "cool" in text.lower():
                            base_temp -= 20
                        elif "hot" in text.lower() or "warm" in text.lower():
                            base_temp += 10
                        mock_temps.append(base_temp)
                    
                    # Create temperature chart
                    fig_temp = go.Figure()
                    fig_temp.add_trace(go.Scatter(
                        x=st.session_state.chart_data["dates"],
                        y=mock_temps,
                        mode='lines+markers',
                        name='Temperature',
                        line=dict(color=st.session_state.theme_color, width=4),
                        marker=dict(size=10)
                    ))
                    
                    fig_temp.update_layout(
                        title="7-Day Temperature Forecast",
                        xaxis_title="Day",
                        yaxis_title=f"Temperature (°{'F' if units.startswith('Imperial') else 'C'})",
                        template="plotly_dark",
                        height=400,
                        margin=dict(l=20, r=20, t=40, b=20),
                    )
                    
                    st.plotly_chart(fig_temp, use_container_width=True)
                    
                    # Create precipitation chart
                    mock_precip = []
                    for i in range(7):
                        if "rain" in text.lower() or "precipitation" in text.lower():
                            mock_precip.append(random.randint(30, 90))
                        else:
                            mock_precip.append(random.randint(0, 40))
                    
                    fig_precip = go.Figure()
                    fig_precip.add_trace(go.Bar(
                        x=st.session_state.chart_data["dates"],
                        y=mock_precip,
                        name='Precipitation Chance',
                        marker_color='rgba(0, 149, 255, 0.7)'
                    ))
                    
                    fig_precip.update_layout(
                        title="Precipitation Probability",
                        xaxis_title="Day",
                        yaxis_title="Probability (%)",
                        template="plotly_dark",
                        height=350,
                        margin=dict(l=20, r=20, t=40, b=20),
                    )
                    
                    st.plotly_chart(fig_precip, use_container_width=True)
                
                with tab4:
                    st.subheader("Air Quality Index")
                    
                    # Get mock air quality data
                    air_data = get_mock_air_quality(location)
                    
                    # Display AQI gauge
                    fig_gauge = go.Figure(go.Indicator(
                        mode = "gauge+number+delta",
                        value = air_data["aqi"],
                        domain = {'x': [0, 1], 'y': [0, 1]},
                        title = {'text': f"Air Quality Index in {location}", 'font': {'size': 24}},
                        delta = {'reference': 100, 'increasing': {'color': "red"}, 'decreasing': {'color': "green"}},
                        gauge = {
                            'axis': {'range': [None, 300], 'tickwidth': 1, 'tickcolor': "white"},
                            'bar': {'color': air_data["color"]},
                            'bgcolor': "white",
                            'borderwidth': 2,
                            'bordercolor': "gray",
                            'steps': [
                                {'range': [0, 50], 'color': 'rgba(0, 255, 0, 0.3)'},
                                {'range': [50, 100], 'color': 'rgba(255, 255, 0, 0.3)'},
                                {'range': [100, 150], 'color': 'rgba(255, 165, 0, 0.3)'},
                                {'range': [150, 200], 'color': 'rgba(255, 0, 0, 0.3)'},
                                {'range': [200, 300], 'color': 'rgba(128, 0, 128, 0.3)'}
                            ],
                            'threshold': {
                                'line': {'color': "red", 'width': 4},
                                'thickness': 0.75,
                                'value': 100
                            }
                        }
                    ))
                    
                    fig_gauge.update_layout(
                        template="plotly_dark",
                        height=300,
                        margin=dict(l=20, r=20, t=60, b=20),
                    )
                    
                    st.plotly_chart(fig_gauge, use_container_width=True)
                    
                    # Display AQI status
                    st.markdown(f"<div style='text-align: center; font-size: 1.5rem; margin-bottom: 20px;'>Status: <span style='color: {air_data['color']};'>{air_data['status']}</span></div>", unsafe_allow_html=True)
                    
                    # Display pollutant levels
                    st.subheader("Pollutant Levels")
                    
                    pollutant_df = pd.DataFrame({
                        "Pollutant": list(air_data["pollutants"].keys()),
                        "Value": list(air_data["pollutants"].values())
                    })
                    
                    fig_pollutants = go.Figure()
                    fig_pollutants.add_trace(go.Bar(
                        x=pollutant_df["Pollutant"],
                        y=pollutant_df["Value"],
                        marker_color=[
                            'rgba(255, 99, 132, 0.8)',
                            'rgba(54, 162, 235, 0.8)',
                            'rgba(255, 206, 86, 0.8)',
                            'rgba(75, 192, 192, 0.8)',
                            'rgba(153, 102, 255, 0.8)',
                            'rgba(255, 159, 64, 0.8)'
                        ]
                    ))
                    
                    fig_pollutants.update_layout(
                        template="plotly_dark",
                        height=350,
                        margin=dict(l=20, r=20, t=40, b=20),
                    )
                    
                    st.plotly_chart(fig_pollutants, use_container_width=True)
                    
                    # Health recommendations based on AQI
                    st.subheader("Health Recommendations")
                    if air_data["status"] == "Good":
                        st.success("Air quality is good. Enjoy outdoor activities!")
                    elif air_data["status"] == "Moderate":
                        st.info("Air quality is acceptable. Unusually sensitive people should consider reducing prolonged outdoor exertion.")
                    elif air_data["status"] == "Unhealthy for Sensitive Groups":
                        st.warning("Members of sensitive groups may experience health effects. The general public is less likely to be affected.")
                    else:
                        st.error("Everyone may begin to experience health effects. Members of sensitive groups may experience more serious health effects.")
                    
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")
            if "403" in str(e) or "401" in str(e):
                st.error("API key error. Please check your Gemini API key.")
            elif "429" in str(e):
                st.error("Rate limit exceeded. Please try again later.")

# Compare Locations Tab Content
elif tabs == "Compare":
    st.markdown(f"<div class='main-title' style='box-shadow: 0px 0px 15px {st.session_state.theme_color};'>🔍 Weather Comparison</div>", unsafe_allow_html=True)
    
    if not selected_locations or len(selected_locations) < 2:
        st.info("Please select at least 2 locations to compare from the sidebar.")
    elif compare_button:
        # Show comparison data
        st.subheader(f"Comparing Weather: {', '.join(selected_locations)}")
        
        # Get comparison data
        comparison_data = compare_locations(selected_locations)
        
        # Create comparison table
        comparison_df = pd.DataFrame(comparison_data)
        st.markdown("<div class='compare-table'>", unsafe_allow_html=True)
        st.table(comparison_df)
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Create bar chart for temperature comparison
        fig_temp_compare = go.Figure()
        for loc in selected_locations:
            # Extract numeric temperature value (remove °F)
            temp_value = int(comparison_data[loc]["temp"].replace("°F", ""))
            fig_temp_compare.add_trace(go.Bar(
                x=[loc],
                y=[temp_value],
                name=loc
            ))
        
        fig_temp_compare.update_layout(
            title="Temperature Comparison",
            yaxis_title="Temperature (°F)",
            template="plotly_dark",
            height=400
        )
        
        st.plotly_chart(fig_temp_compare, use_container_width=True)
        
        # Create radar chart for full comparison
        categories = ['Temperature', 'Humidity', 'Wind Speed', 'Precipitation']
        
        fig_radar = go.Figure()
        
        for loc in selected_locations:
            # Normalize values for radar chart
            temp_value = int(comparison_data[loc]["temp"].replace("°F", ""))
            humid_value = int(comparison_data[loc]["humidity"].replace("%", ""))
            wind_value = int(comparison_data[loc]["wind"].split(" ")[0])
            precip_value = int(comparison_data[loc]["precip"].replace("%", ""))
            
            # Normalize values between 0-100
            temp_norm = min(100, max(0, ((temp_value - 30) / 70) * 100))
            
            fig_radar.add_trace(go.Scatterpolar(
                r=[temp_norm, humid_value, wind_value, precip_value],
                theta=categories,
                fill='toself',
                name=loc
            ))
        
        fig_radar.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 100]
                )
            ),
            template="plotly_dark",
            height=500
        )
        
        st.plotly_chart(fig_radar, use_container_width=True)
        
        # Weather alerts comparison
        st.subheader("Weather Alerts")
        
        for loc in selected_locations:
            has_alert = random.choice([True, False])
            if has_alert:
                alert_type = random.choice(["Heavy Rain", "Strong Wind", "Heat Warning", "Storm Warning"])
                st.warning(f"{loc}: {alert_type}")
            else:
                st.success(f"{loc}: No weather alerts")

# Historical Data Tab Content
elif tabs == "Historical Data":
    st.markdown(f"<div class='main-title' style='box-shadow: 0px 0px 15px {st.session_state.theme_color};'>📊 Historical Weather Data</div>", unsafe_allow_html=True)
    
    if not location_hist:
        st.info("Please select a location from the sidebar.")
    elif view_historical:
        st.subheader(f"Historical Weather Data for {location_hist} ({year})")
        
        # Get mock historical data
        hist_data = get_mock_historical_data(location_hist)
        
        # Create yearly temperature trend chart
        fig_hist_temp = go.Figure()
        fig_hist_temp.add_trace(go.Scatter(
            x=hist_data["months"],
            y=hist_data["avg_temps"],
            mode='lines+markers',
            name='Avg Temperature',
            line=dict(color=st.session_state.theme_color, width=3)
        ))
        
        fig_hist_temp.update_layout(
            title=f"Average Monthly Temperatures in {year}",
            xaxis_title="Month",
            yaxis_title="Temperature (°F)",
            template="plotly_dark",
            height=400
        )
        
        st.plotly_chart(fig_hist_temp, use_container_width=True)
        
        # Create precipitation chart
        fig_hist_precip = go.Figure()
        fig_hist_precip.add_trace(go.Bar(
            x=hist_data["months"],
            y=hist_data["avg_precip"],
            name='Precipitation',
            marker_color='rgba(0, 149, 255, 0.7)'
        ))
        
        fig_hist_precip.update_layout(
            title=f"Average Monthly Precipitation in {year}",
            xaxis_title="Month",
            yaxis_title="Precipitation (mm)",
            template="plotly_dark",
            height=400
        )
        
        st.plotly_chart(fig_hist_precip, use_container_width=True)
        
        # Create a year-over-year comparison (mock data)
        st.subheader("Year-over-Year Comparison")
        
        # Create mock data for previous years
        years = [year-2, year-1, year]
        yearly_avg_temp = [random.uniform(60, 75) for _ in range(3)]
        yearly_avg_precip = [random.uniform(700, 1200) for _ in range(3)]
        
        # Create a 2-column layout
        col1, col2 = st.columns(2)
        
        with col1:
            fig_yoy_temp = go.Figure()
            fig_yoy_temp.add_trace(go.Bar(
                x=years,
                y=yearly_avg_temp,
                marker_color='rgba(255, 126, 0, 0.7)'
            ))
            
            fig_yoy_temp.update_layout(
                title="Yearly Average Temperature",
                xaxis_title="Year",
                yaxis_title="Temperature (°F)",
                template="plotly_dark",
                height=350
            )
            
            st.plotly_chart(fig_yoy_temp, use_container_width=True)
        
        with col2:
            fig_yoy_precip = go.Figure()
            fig_yoy_precip.add_trace(go.Bar(
                x=years,
                y=yearly_avg_precip,
                marker_color='rgba(0, 149, 255, 0.7)'
            ))
            
            fig_yoy_precip.update_layout(
                title="Yearly Total Precipitation",
                xaxis_title="Year",
                yaxis_title="Precipitation (mm)",
                template="plotly_dark",
                height=350
            )
            
            st.plotly_chart(fig_yoy_precip, use_container_width=True)
        
        # Add weather extremes for the year
        st.subheader(f"Weather Extremes in {year}")
        
        extremes_data = {
            "Event": ["Highest Temperature", "Lowest Temperature", "Highest Precipitation", "Strongest Wind"],
            "Value": [f"{random.randint(90, 110)}°F", f"{random.randint(-10, 30)}°F", f"{random.randint(3, 12)} inches", f"{random.randint(40, 80)} mph"],
            "Date": [f"{random.choice(['Jun', 'Jul', 'Aug'])} {random.randint(1, 30)}, {year}", 
                     f"{random.choice(['Dec', 'Jan', 'Feb'])} {random.randint(1, 28)}, {year}",
                     f"{random.choice(['Mar', 'Apr', 'Sep'])} {random.randint(1, 30)}, {year}",
                     f"{random.choice(['Oct', 'Nov', 'Dec'])} {random.randint(1, 30)}, {year}"]
        }
        
        extremes_df = pd.DataFrame(extremes_data)
        st.table(extremes_df)

# Footer with Features Summary
st.markdown("---")
with st.expander("✨ New Features"):
    st.markdown("""
    <div class='feature-card'>
        <h4>1. User Profiles & Settings Manager</h4>
        <p>Save your favorite locations, preferred units, and personalize your experience.</p>
    </div>
    
    <div class='feature-card'>
        <h4>2. Interactive Weather Map</h4>
        <p>Visualize weather patterns and systems on an interactive map with markers and layers.</p>
    </div>
    
    <div class='feature-card'>
        <h4>3. API Key Management & Memory</h4>
        <p>Securely save your API key for future sessions to streamline your experience.</p>
    </div>
    
    <div class='feature-card'>
        <h4>4. Enhanced Location Selector with Favorites</h4>
        <p>Quickly access your favorite locations and add new ones with a single click.</p>
    </div>
    
    <div class='feature-card'>
        <h4>5. Units Toggle (°C/°F)</h4>
        <p>Switch between metric and imperial units based on your preference.</p>
    </div>
    
    <div class='feature-card'>
        <h4>6. Multi-language Support</h4>
        <p>View key weather terms in your preferred language with translations for major languages.</p>
    </div>
    
    <div class='feature-card'>
        <h4>7. Theme Customization</h4>
        <p>Personalize your experience with different theme colors to match your style.</p>
    </div>
    
    <div class='feature-card'>
        <h4>8. Location Comparison</h4>
        <p>Compare weather conditions across multiple locations side by side.</p>
    </div>
    
    <div class='feature-card'>
        <h4>9. Advanced Weather Visualization</h4>
        <p>View detailed charts, graphs, and air quality information with interactive elements.</p>
    </div>
    
    <div class='feature-card'>
        <h4>10. Historical Weather Data</h4>
        <p>Access and analyze historical weather patterns for your locations of interest.</p>
    </div>
    """, unsafe_allow_html=True)

st.caption("✨ Powered by Gemini 2.0 Flash | Pro Edition | Dark Mode Activated 🌌")

# Show notifications if needed
if st.session_state.show_notification:
    st.markdown(f"""
        <div class='notification'>
            {st.session_state.notification_message}
        </div>
    """, unsafe_allow_html=True)
    # Reset notification after showing
    st.session_state.show_notification = False
