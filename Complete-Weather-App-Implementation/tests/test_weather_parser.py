"""Unit tests for weather_parser module."""

import pytest
from weather_parser import parse_weather_data, get_weather_icon


class TestWeatherParser:
    """Test cases for weather data parsing."""
    
    def test_parse_valid_weather_data(self):
        """Test parsing valid JSON weather data."""
        sample_json = {
            "main": {
                "temp": 22.5,
                "feels_like": 21.0,
                "humidity": 65
            },
            "weather": [
                {
                    "main": "Clear",
                    "description": "clear sky"
                }
            ],
            "name": "London",
            "sys": {
                "country": "GB"
            }
        }
        
        result = parse_weather_data(sample_json)
        
        assert result is not None
        assert result["temperature"] == 22.5
        assert result["condition"] == "clear sky"
        assert result["feels_like"] == 21.0
        assert result["humidity"] == 65
        assert result["city_name"] == "London"
        assert result["country"] == "GB"
    
    def test_parse_missing_main_data(self):
        """Test handling of missing main section."""
        sample_json = {
            "weather": [{"main": "Clear"}],
            "name": "Paris"
        }
        
        result = parse_weather_data(sample_json)
        assert result is None
    
    def test_parse_missing_weather_data(self):
        """Test handling of missing weather section."""
        sample_json = {
            "main": {"temp": 22.5},
            "name": "Paris"
        }
        
        result = parse_weather_data(sample_json)
        assert result is None
    
    def test_parse_empty_json(self):
        """Test handling of empty JSON."""
        result = parse_weather_data({})
        assert result is None
    
    def test_parse_none_input(self):
        """Test handling of None input."""
        result = parse_weather_data(None)
        assert result is None
    
    def test_get_weather_icon(self):
        """Test weather icon mapping."""
        assert get_weather_icon("Clear") == "☀️"
        assert get_weather_icon("Rain") == "🌧️"
        assert get_weather_icon("Snow") == "❄️"
        assert get_weather_icon("Unknown") == "🌡️"