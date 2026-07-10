def get_weather_forecast(destination: str):
    """
    Retrieves weather forecast for the destination.
    Uses seasonal defaults for tourist places.
    """
    dest = (destination or "").strip().lower()
    
    if "goa" in dest:
        return {
            "temp_c": 31,
            "condition": "Humid and sunny",
            "forecast": [
                {"day": "Day 1", "temp": "30°C - 32°C", "condition": "Partly Cloudy"},
                {"day": "Day 2", "temp": "29°C - 31°C", "condition": "Scattered Showers"},
                {"day": "Day 3", "temp": "30°C - 32°C", "condition": "Sunny"},
                {"day": "Day 4", "temp": "31°C - 33°C", "condition": "Sunny"},
                {"day": "Day 5", "temp": "30°C - 32°C", "condition": "Humid and Sunny"}
            ],
            "recommendation": "Carry light cotton clothing, sunscreen, and beach wear. Keep an umbrella handy."
        }
    elif "tokyo" in dest or "japan" in dest:
        return {
            "temp_c": 18,
            "condition": "Mild and pleasant",
            "forecast": [
                {"day": "Day 1", "temp": "15°C - 19°C", "condition": "Sunny"},
                {"day": "Day 2", "temp": "14°C - 18°C", "condition": "Clear"},
                {"day": "Day 3", "temp": "13°C - 17°C", "condition": "Light Rain"},
                {"day": "Day 4", "temp": "15°C - 20°C", "condition": "Windy and Sunny"},
                {"day": "Day 5", "temp": "16°C - 20°C", "condition": "Overcast"}
            ],
            "recommendation": "Comfortable light jacket, sneakers for walking, and layering items."
        }
    else:
        return {
            "temp_c": 25,
            "condition": "Clear skies",
            "forecast": [
                {"day": "Day 1", "temp": "22°C - 26°C", "condition": "Sunny"},
                {"day": "Day 2", "temp": "21°C - 25°C", "condition": "Clear"},
                {"day": "Day 3", "temp": "23°C - 27°C", "condition": "Clear"},
                {"day": "Day 4", "temp": "22°C - 26°C", "condition": "Sunny"},
                {"day": "Day 5", "temp": "22°C - 26°C", "condition": "Sunny"}
            ],
            "recommendation": "Carry comfortable outfits suitable for sightseeing. Check local guidelines before travel."
        }
