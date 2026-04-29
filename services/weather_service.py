import requests

API_KEY = "cf042dec1cc58e14c32de4a7f21e2ee6" 

def get_weather_by_coords(lat, lon):
    """
    Fetches raw weather fields: city, temperature, humidity, and rainfall. No classification.
    """
    # Current weather
    url = f"http://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={API_KEY}&units=metric"
    try:
        # Added strict timeout to prevent hanging the web app if the weather API is slow
        data = requests.get(url, timeout=5).json()
        temp = data['main']['temp']
        humidity = data['main']['humidity']
        city = data.get("name", "Unknown")

        # Forecast rainfall for next few hours
        forecast_url = f"http://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}&appid={API_KEY}&units=metric"
        forecast = requests.get(forecast_url, timeout=5).json()
        
        rainfall = 0
        if 'list' in forecast:
            for item in forecast['list'][:8]:
                rainfall += item.get('rain', {}).get('3h', 0)

        return city, temp, humidity, rainfall
    except Exception as e:
        # Provide sensible default if API fails
        print("OpenWeather Error:", e)
        return "Unknown", 25.0, 60.0, 0.0