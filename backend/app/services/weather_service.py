import httpx
from typing import Optional, Dict, Any
from core.config import settings

class WeatherService:
    def __init__(self):
        self.api_key = settings.OPENWEATHER_API_KEY
        self.base_url = "https://api.openweathermap.org/data/2.5/weather"

    async def get_weather(self, location: str) -> Dict[str, Any]:
        """
        Get weather for a location. 
        If no API key provided, returns mock data for Togo region.
        """
        if not self.api_key:
            return self._get_mock_weather(location)

        try:
            async with httpx.AsyncClient() as client:
                params = {
                    "q": location,
                    "appid": self.api_key,
                    "units": "metric",
                    "lang": "fr"
                }
                response = await client.get(self.base_url, params=params)
                if response.status_code == 200:
                    data = response.json()
                    return data
                else:
                    return self._get_mock_weather(location, error=f"API Error: {response.status_code}")
        except Exception as e:
            return self._get_mock_weather(location, error=str(e))

    def _get_mock_weather(self, location: str, error: Optional[str] = None) -> Dict[str, Any]:
        return {
            "name": location,
            "main": {"temp": 28.5, "humidity": 65},
            "weather": [{"description": "Partiellement nuageux", "icon": "02d"}],
            "mock": True,
            "error_detail": error
        }

weather_service = WeatherService()
