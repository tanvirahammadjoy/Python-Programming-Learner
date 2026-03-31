"""Parses JSON weather data and extracts relevant information."""

import logging
from typing import Dict, Any, Optional

# Configure logging
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)


def parse_weather_data(json_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Parse raw JSON weather data into standardized format.
    
    Args:
        json_data: Raw JSON response from weather API
        
    Returns:
        Standardized dictionary with temperature, condition, feels_like, humidity
        Returns None if critical data is missing
    """
    if not json_data:
        logger.warning("Empty JSON data provided")
        return None
    
    try:
        # Extract main weather data
        main_data = json_data.get("main", {})
        weather_list = json_data.get("weather", [])
        
        if not main_data:
            logger.warning("Missing 'main' section in weather data")
            return None
        
        if not weather_list:
            logger.warning("Missing 'weather' section in weather data")
            return None
        
        # Get primary weather condition
        weather_info = weather_list[0]
        
        # Build standardized response
        standardized = {
            "temperature": main_data.get("temp"),
            "condition": weather_info.get("description", "Unknown"),
            "condition_code": weather_info.get("main", "Unknown"),
            "feels_like": main_data.get("feels_like"),
            "humidity": main_data.get("humidity"),
            "city_name": json_data.get("name", "Unknown"),
            "country": json_data.get("sys", {}).get("country", "")
        }
        
        # Validate required fields
        if standardized["temperature"] is None:
            logger.error("Temperature data missing from response")
            return None
        
        if standardized["condition"] == "Unknown":
            logger.warning("Weather condition description missing")
        
        return standardized
        
    except (KeyError, TypeError, IndexError) as e:
        logger.error(f"Failed to parse JSON data: {str(e)}")
        return None


def get_weather_icon(condition_code: str) -> str:
    """
    Map weather condition to emoji icon.
    
    Args:
        condition_code: Main weather condition (e.g., "Clear", "Rain")
        
    Returns:
        Emoji representing the weather
    """
    icons = {
        "Clear": "☀️",
        "Clouds": "☁️",
        "Rain": "🌧️",
        "Drizzle": "🌦️",
        "Thunderstorm": "⛈️",
        "Snow": "❄️",
        "Mist": "🌫️",
        "Fog": "🌫️",
        "Smoke": "💨",
        "Haze": "🌫️",
        "Dust": "💨",
        "Sand": "💨",
        "Ash": "🌋",
        "Squall": "💨",
        "Tornado": "🌪️"
    }
    return icons.get(condition_code, "🌡️")


def format_weather_display(weather_data: Dict[str, Any], units: str = "metric") -> str:
    """
    Format weather data for user-friendly display.
    
    Args:
        weather_data: Standardized weather dictionary from parse_weather_data
        units: "metric" (Celsius) or "imperial" (Fahrenheit)
        
    Returns:
        Formatted string for display
    """
    if not weather_data:
        return "Unable to display weather data."
    
    temp = weather_data["temperature"]
    condition = weather_data["condition"].capitalize()
    feels_like = weather_data["feels_like"]
    humidity = weather_data["humidity"]
    city = weather_data["city_name"]
    country = weather_data["country"]
    icon = get_weather_icon(weather_data["condition_code"])
    
    temp_unit = "°C" if units == "metric" else "°F"
    
    # Build display string
    location = f"{city}, {country}" if country else city
    
    display = f"""
{icon} Weather in {location}
{'-' * 30}
🌡️ Temperature: {temp:.1f}{temp_unit}
✨ Condition: {condition}
🌡️ Feels like: {feels_like:.1f}{temp_unit}
💧 Humidity: {humidity}%
"""
    return display.strip()