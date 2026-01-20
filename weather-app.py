import streamlit as st
import requests
import pandas as pd
import matplotlib.pyplot as plt

# ---------------- CONFIG ----------------
API_KEY = "df182bd2da8f49509e884711262001"
BASE_URL = "http://api.weatherapi.com/v1/forecast.json"

# ---------------- FUNCTIONS ----------------
def get_weather(city):
    params = {
        "key": API_KEY,
        "q": city,
        "days": 7,
        "aqi": "yes",
        "alerts": "yes"
    }
    r = requests.get(BASE_URL, params=params)
    return r.json()

def smart_summary(data):
    temp = data["current"]["temp_c"]
    rain = data["forecast"]["forecastday"][0]["day"]["daily_chance_of_rain"]
    wind = data["current"]["wind_kph"]

    if rain > 60:
        return "High chance of rain today 🌧️ Bring an umbrella!"
    elif temp > 25:
        return "It's warm and sunny ☀️ Stay hydrated!"
    elif temp < 5:
        return "Cold conditions 🥶 Dress warmly!"
    elif wind > 30:
        return "Windy today 🌬️ Hold onto your hat!"
    else:
        return "Pleasant weather today 🌤️"

def clothing_advice(temp):
    if temp < 5:
        return "🧥 Heavy jacket recommended"
    elif temp < 15:
        return "🧣 Light jacket suggested"
    elif temp < 25:
        return "👕 Comfortable clothes"
    else:
        return "🩳 Shorts & sunscreen!"

def activity_advice(condition):
    if "rain" in condition.lower():
        return "🎬 Good day for indoor activities"
    elif "sun" in condition.lower():
        return "🏃 Perfect for outdoor sports"
    elif "snow" in condition.lower():
        return "⛄ Great for winter fun"
    else:
        return "🚶 Nice for a walk"

def plot_hourly(data):
    hours = data["forecast"]["forecastday"][0]["hour"]
    times = [h["time"].split(" ")[1] for h in hours]
    temps = [h["temp_c"] for h in hours]

    plt.figure()
    plt.plot(times, temps)
    plt.xticks(rotation=90)
    plt.title("24 Hour Temperature")
    plt.xlabel("Time")
    plt.ylabel("°C")
    st.pyplot(plt)

# ---------------- UI ----------------
st.set_page_config(page_title="Pro Weather App", layout="wide")
st.title("🌍 Smart Weather Dashboard")

tab1, tab2 = st.tabs(["🌤 City Weather", "✈️ Travel Compare"])

# -------- CITY WEATHER --------
with tab1:
    city = st.text_input("Enter a city:")

    if st.button("Get Weather"):
        data = get_weather(city)

        if "error" in data:
            st.error("City not found")
        else:
            current = data["current"]
            forecast = data["forecast"]["forecastday"]

            st.subheader(f"📍 {data['location']['name']}, {data['location']['country']}")

            col1, col2, col3 = st.columns(3)
            col1.metric("Temperature", f"{current['temp_c']}°C")
            col2.metric("Feels Like", f"{current['feelslike_c']}°C")
            col3.metric("Humidity", f"{current['humidity']}%")

            st.info(smart_summary(data))
            st.success(clothing_advice(current["temp_c"]))
            st.warning(activity_advice(current["condition"]["text"]))

            # -------- HOURLY GRAPH --------
            st.subheader("📈 Hourly Temperature")
            plot_hourly(data)

            # -------- 7 DAY FORECAST --------
            st.subheader("🗓 7 Day Forecast")
            cols = st.columns(7)

            for i, day in enumerate(forecast):
                with cols[i]:
                    st.write(day["date"])
                    st.image("https:" + day["day"]["condition"]["icon"])
                    st.write(f"{day['day']['maxtemp_c']}°C / {day['day']['mintemp_c']}°C")
                    st.write(f"Rain: {day['day']['daily_chance_of_rain']}%")

            # -------- AIR QUALITY --------
            st.subheader("🌫 Air Quality")
            aqi = current["air_quality"]
            st.write("PM2.5:", round(aqi["pm2_5"],2))
            st.write("PM10:", round(aqi["pm10"],2))
            st.write("CO:", round(aqi["co"],2))

            # -------- ALERTS --------
            if data["alerts"]["alert"]:
                st.subheader("⚠️ Weather Alerts")
                for alert in data["alerts"]["alert"]:
                    st.error(alert["headline"])

# -------- TRAVEL MODE --------
with tab2:
    st.subheader("Compare Two Cities")

    c1 = st.text_input("City 1")
    c2 = st.text_input("City 2")

    if st.button("Compare"):
        d1 = get_weather(c1)
        d2 = get_weather(c2)

        if "error" in d1 or "error" in d2:
            st.error("One city not found")
        else:
            col1, col2 = st.columns(2)

            with col1:
                st.subheader(c1)
                st.metric("Temp", f"{d1['current']['temp_c']}°C")
                st.write(d1["current"]["condition"]["text"])

            with col2:
                st.subheader(c2)
                st.metric("Temp", f"{d2['current']['temp_c']}°C")
                st.write(d2["current"]["condition"]["text"])
