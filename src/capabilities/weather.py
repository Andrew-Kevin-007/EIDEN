"""Weather information capabilities."""
import requests
from typing import Dict, Any, Optional
from datetime import datetime


class WeatherService:
    """Get weather information using wttr.in (no API key needed)."""
    
    def __init__(self):
        """Initialize weather service."""
        self.base_url = "https://wttr.in"
    
    def get_weather(self, location: Optional[str] = None) -> Dict[str, Any]:
        """
        Get current weather information.
        
        Args:
            location: Location name (default: auto-detect from IP)
            
        Returns:
            Result dictionary with weather data
        """
        try:
            # Use wttr.in - simple weather API that doesn't need API key
            location_param = location if location else ""
            url = f"{self.base_url}/{location_param}?format=j1"
            
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                # Extract current conditions
                current = data['current_condition'][0]
                location_info = data['nearest_area'][0]
                
                temp_c = current['temp_C']
                temp_f = current['temp_F']
                condition = current['weatherDesc'][0]['value']
                feels_like_c = current['FeelsLikeC']
                feels_like_f = current['FeelsLikeF']
                humidity = current['humidity']
                wind_speed = current['windspeedKmph']
                
                location_name = location_info['areaName'][0]['value']
                country = location_info['country'][0]['value']
                
                weather_text = (
                    f"Weather in {location_name}, {country}: "
                    f"{condition}, {temp_f}°F ({temp_c}°C). "
                    f"Feels like {feels_like_f}°F. "
                    f"Humidity {humidity}%, Wind {wind_speed} km/h."
                )
                
                return {
                    "success": True,
                    "message": weather_text,
                    "data": {
                        "location": f"{location_name}, {country}",
                        "temperature_f": temp_f,
                        "temperature_c": temp_c,
                        "condition": condition,
                        "feels_like_f": feels_like_f,
                        "humidity": humidity,
                        "wind_speed": wind_speed
                    }
                }
            else:
                return {
                    "success": False,
                    "message": "Could not retrieve weather information"
                }
                
        except Exception as e:
            return {
                "success": False,
                "message": f"Weather service error: {str(e)}"
            }
    
    def get_forecast(self, location: Optional[str] = None, days: int = 3) -> Dict[str, Any]:
        """
        Get weather forecast.
        
        Args:
            location: Location name
            days: Number of days (1-3)
            
        Returns:
            Result dictionary with forecast data
        """
        try:
            location_param = location if location else ""
            url = f"{self.base_url}/{location_param}?format=j1"
            
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                weather_data = data['weather'][:days]
                
                forecast_text = f"Forecast for {location if location else 'your location'}:\n"
                
                for day_data in weather_data:
                    date = day_data['date']
                    max_temp_f = day_data['maxtempF']
                    min_temp_f = day_data['mintempF']
                    condition = day_data['hourly'][0]['weatherDesc'][0]['value']
                    
                    forecast_text += f"{date}: {condition}, High {max_temp_f}°F, Low {min_temp_f}°F. "
                
                return {
                    "success": True,
                    "message": forecast_text
                }
            else:
                return {
                    "success": False,
                    "message": "Could not retrieve forecast"
                }
                
        except Exception as e:
            return {
                "success": False,
                "message": f"Forecast error: {str(e)}"
            }
