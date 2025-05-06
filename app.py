import streamlit as st
import google.generativeai as genai
import os
from datetime import datetime, timedelta

st.set_page_config(
    page_title="AI Weather Assistant",
    page_icon="🌤️",
    layout="wide"
)

# Sidebar for API key input
with st.sidebar:
    st.title("🌤️ AI Weather")
    api_key = st.text_input("Enter Gemini API Key", type="password")
    st.caption("Your API key is kept private and not stored")
    
    # Input for location
    location = st.text_input("Enter location", placeholder="New York, Paris, Tokyo...")
    
    # Time frame selection
    time_frame = st.selectbox(
        "Select time frame",
        ["Current weather", "Today's forecast", "Weekly forecast"]
    )
    
    # Additional options
    show_details = st.checkbox("Show detailed information", value=True)
    
    # Submit button
    submit = st.button("Get Weather Info")

# Main content area
st.title("AI Weather Assistant")

if not api_key:
    st.info("Please enter your Gemini API key in the sidebar to start.")
elif not location:
    st.info("Enter a location in the sidebar to get weather information.")
elif submit:
    try:
        # Configure the Gemini API
        genai.configure(api_key=api_key)
        
        # Create a model instance
        model = genai.GenerativeModel(model_name="gemini-2.0-flash")
        
        with st.spinner("Fetching weather information..."):
            # Current date and time
            now = datetime.now()
            today_str = now.strftime("%A, %d %B %Y")  # e.g., Monday, 06 May 2025
            
            # Date description based on user choice
            if time_frame == "Current weather":
                date_info = f"as of now ({today_str})"
            elif time_frame == "Today's forecast":
                date_info = f"for today ({today_str})"
            elif time_frame == "Weekly forecast":
                week_dates = [(now + timedelta(days=i)).strftime("%A, %d %B") for i in range(7)]
                date_info = f"for the upcoming week ({', '.join(week_dates)})"
            
            detail_level = "detailed" if show_details else "brief"

            # Prompt construction
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

            # Generate the response
            response = model.generate_content(prompt)
            
            # Display location and time frame
            st.subheader(f"{location} - {time_frame}")
            
            # Display the weather information
            st.markdown(response.text)
            
            # Add visual representation
            col1, col2 = st.columns([3, 1])
            with col2:
                st.caption("Weather visualization")
                weather_emoji = "🌤️"  # Default emoji
                
                if "rain" in response.text.lower():
                    weather_emoji = "🌧️"
                elif "cloud" in response.text.lower():
                    weather_emoji = "☁️"
                elif "sunny" in response.text.lower() or "clear" in response.text.lower():
                    weather_emoji = "☀️"
                elif "snow" in response.text.lower():
                    weather_emoji = "❄️"
                elif "storm" in response.text.lower() or "thunder" in response.text.lower():
                    weather_emoji = "⛈️"
                
                st.markdown(f"<h1 style='text-align: center; font-size: 5rem;'>{weather_emoji}</h1>", unsafe_allow_html=True)

    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
        if "403" in str(e) or "401" in str(e):
            st.error("API key error. Please check your Gemini API key.")
        elif "429" in str(e):
            st.error("Rate limit exceeded. Please try again later.")

# Footer
st.markdown("---")
st.caption("AI Weather Assistant uses Google's Gemini-2.0-Flash model to provide weather information.")
