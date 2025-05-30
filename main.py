from sense_hat import SenseHat
import requests
from dataclasses import dataclass
from typing import Optional

@dataclass
class WeatherAlert:
    city: str
    state: str
    latitude: float
    longitude: float
    headline: str
    event: str
    severity: str
    urgency: str
    expires: str
    description: str
    instruction: str

def print_test():

    sense.show_message("Hello World")

def main():
    state: str = "ga"
    city: str = "atlanta"
    url: str = f"http://rpi02w.local:8080/weather-alert/{state}/{city}"
    weather_alert = get_weather_alert(url)
    if weather_alert and weather_alert.event:
        sense.show_message(weather_alert.event)
    else:
        print("No weather alert found")


def get_weather_alert(url) -> Optional[WeatherAlert]:
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        return WeatherAlert(**data)
    except (requests.RequestException, ValueError) as e:
        print(f"Error fetching weather alert: {e}")
        return None


if __name__ == "__main__":
    sense = SenseHat()
    sense.rotation = 90
    main()


