"""Simple caching mechanism to reduce API calls."""

import time
from typing import Dict, Any, Optional
from datetime import datetime, timedelta


class WeatherCache:
    """Cache weather data with time-based expiration."""
    
    def __init__(self, ttl_minutes: int = 5):
        """
        Initialize cache.
        
        Args:
            ttl_minutes: How long to keep cached data (default: 5 minutes)
        """
        self._cache: Dict[str, Dict[str, Any]] = {}
        self.ttl = timedelta(minutes=ttl_minutes)
    
    def get(self, city: str) -> Optional[Dict[str, Any]]:
        """
        Get cached weather data for a city if still valid.
        
        Args:
            city: City name (case-insensitive)
            
        Returns:
            Cached data if exists and not expired, else None
        """
        city_key = city.lower().strip()
        
        if city_key in self._cache:
            cached_entry = self._cache[city_key]
            cached_time = cached_entry["timestamp"]
            
            if datetime.now() - cached_time < self.ttl:
                print(f"📦 Using cached data for '{city}' (less than {self.ttl.seconds//60} minutes old)")
                return cached_entry["data"]
            else:
                # Cache expired
                del self._cache[city_key]
        
        return None
    
    def set(self, city: str, data: Dict[str, Any]) -> None:
        """
        Store weather data in cache.
        
        Args:
            city: City name
            data: Weather data to cache
        """
        city_key = city.lower().strip()
        self._cache[city_key] = {
            "data": data,
            "timestamp": datetime.now()
        }
    
    def clear(self) -> None:
        """Clear all cached data."""
        self._cache.clear()
        print("🧹 Cache cleared")
    
    def get_cache_size(self) -> int:
        """Get number of items in cache."""
        return len(self._cache)