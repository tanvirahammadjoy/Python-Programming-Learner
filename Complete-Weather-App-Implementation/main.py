"""Main orchestration module for the Weather App."""

import sys
from typing import Optional
from api_client import WeatherAPIClient
from weather_parser import parse_weather_data, format_weather_display
from cache import WeatherCache


class WeatherApp:
    """Main application orchestrator for weather lookup."""
    
    def __init__(self, use_cache: bool = True):
        """
        Initialize the weather app.
        
        Args:
            use_cache: Enable/disable caching (default: True)
        """
        self.api_client = WeatherAPIClient()
        self.cache = WeatherCache() if use_cache else None
        self.units = "metric"  # Using Celsius
    
    def get_weather(self, city: str) -> Optional[dict]:
        """
        Get weather data for a city (with optional caching).
        
        Args:
            city: City name
            
        Returns:
            Standardized weather data or None if error
        """
        # Check cache first
        if self.cache:
            cached_data = self.cache.get(city)
            if cached_data:
                return cached_data
        
        # Fetch from API
        raw_data = self.api_client.fetch_weather(city, self.units)
        
        if not raw_data:
            return None
        
        # Parse data
        parsed_data = parse_weather_data(raw_data)
        
        if parsed_data and self.cache:
            # Cache successful result
            self.cache.set(city, parsed_data)
        
        return parsed_data
    
    def display_weather(self, city: str) -> bool:
        """
        Fetch and display weather for a city.
        
        Args:
            city: City name
            
        Returns:
            True if successful, False otherwise
        """
        # Input validation
        if not city or not city.strip():
            print("❌ City name cannot be empty.")
            return False
        
        city = city.strip()
        
        # Get weather data
        weather_data = self.get_weather(city)
        
        if not weather_data:
            return False
        
        # Format and display
        display_text = format_weather_display(weather_data, self.units)
        print(f"\n{display_text}\n")
        return True
    
    def run_interactive(self):
        """Run interactive command-line interface."""
        print("\n" + "="*50)
        print("🌤️  WEATHER APP")
        print("="*50)
        print("Enter city names to get weather information.")
        print("Type 'quit', 'exit', or 'q' to exit.")
        print("Type 'clear cache' to clear cached data.")
        print("-"*50)
        
        while True:
            try:
                # Get user input
                user_input = input("\n📍 Enter city name: ").strip()
                
                # Check exit conditions
                if user_input.lower() in ['quit', 'exit', 'q']:
                    print("\n👋 Goodbye!")
                    break
                
                # Handle special commands
                if user_input.lower() == 'clear cache':
                    if self.cache:
                        self.cache.clear()
                        print("✅ Cache cleared successfully!")
                    else:
                        print("ℹ️ Caching is disabled.")
                    continue
                
                # Normal weather lookup
                if not user_input:
                    print("❌ Please enter a city name.")
                    continue
                
                self.display_weather(user_input)
                
            except KeyboardInterrupt:
                print("\n\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"❌ Unexpected error: {str(e)}")
                print("Please try again.")


def main():
    """Entry point for the weather application."""
    app = WeatherApp(use_cache=True)
    app.run_interactive()


if __name__ == "__main__":
    main()