"""Handles all external API requests for weather data."""

import os
import requests
from typing import Optional, Dict, Any
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class WeatherAPIClient:
    """Client for interacting with OpenWeatherMap API."""
    
    BASE_URL = "http://api.openweathermap.org/data/2.5/weather"
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the API client.
        
        Args:
            api_key: OpenWeatherMap API key. If not provided, reads from .env.
        """
        self.api_key = api_key or os.getenv("WEATHER_API_KEY")
        if not self.api_key:
            raise ValueError(
                "API key not found. Please set WEATHER_API_KEY in .env file"
            )
    
    def fetch_weather(self, city: str, units: str = "metric") -> Optional[Dict[str, Any]]:
        """
        Fetch weather data for a given city.
        
        Args:
            city: City name (e.g., "London", "New York")
            units: "metric" for Celsius, "imperial" for Fahrenheit
            
        Returns:
            Dictionary with raw API response, or None if error
            
        Raises:
            ConnectionError: If network issues occur
            ValueError: If invalid response received
        """
        params = {
            "q": city,
            "appid": self.api_key,
            "units": units
        }
        
        try:
            print(f"🌐 Fetching weather data for '{city}'...")
            response = requests.get(
                self.BASE_URL, 
                params=params, 
                timeout=10  # 10 second timeout
            )
            
            # Handle different HTTP status codes
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 401:
                raise ValueError("Invalid API key. Please check your .env file")
            elif response.status_code == 404:
                print(f"❌ City '{city}' not found. Please check the spelling.")
                return None
            elif response.status_code == 429:
                print("❌ Rate limit exceeded. Please try again later.")
                return None
            else:
                print(f"❌ API error: HTTP {response.status_code}")
                return None
                
        except requests.exceptions.Timeout:
            print("❌ Request timeout. Please check your internet connection.")
            return None
        except requests.exceptions.ConnectionError:
            print("❌ No internet connection. Please check your network.")
            return None
        except requests.exceptions.RequestException as e:
            print(f"❌ Request failed: {str(e)}")
            return None


def get_api_client() -> WeatherAPIClient:
    """Factory function to create an API client instance."""
    return WeatherAPIClient()