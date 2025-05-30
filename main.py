import datetime
from time import sleep
import os.path

from sense_hat import SenseHat
import requests
from dataclasses import dataclass
from typing import Optional

recheck_seconds = 300  # 5 minutes
persistent_message = ""

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
    next_check: datetime = datetime.datetime.now()
    while True:
        while datetime.datetime.now() <= next_check:
            sleep(5)
        process_alerts()
        next_check = datetime.datetime.now() + datetime.timedelta(seconds=recheck_seconds)


def process_alerts():
    config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config.txt')
    with open(config_path, 'r') as file:
        state, city = file.read().strip().split('\n')
    url: str = f"http://rpi02w.local:8080/weather-alert/{state}/{city}"
    weather_alert = get_weather_alert(url)
    sense.clear()
    if weather_alert:
        if weather_alert.event:
            alert_color = get_alert_color(weather_alert.severity, weather_alert.urgency)
            sense.show_message(weather_alert.event, text_colour=alert_color)
            sense.show_letter(persistent_message, text_colour=alert_color)
        else:
            pass

def get_weather_alert(url) -> Optional[WeatherAlert]:
    global recheck_seconds
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        return WeatherAlert(**data)
    except (requests.RequestException, ValueError) as e:
        print(f"Error fetching weather alert: {e}")
        recheck_seconds = 30
        return None


def get_alert_color(severity, urgency):
    global recheck_seconds, persistent_message
    recheck_seconds = 300 # five minutes
    persistent_message = ""
    severity = severity.lower()
    urgency = urgency.lower()
    if severity == "extreme":  # red
        recheck_seconds = 15
        persistent_message = "!"
        return [255, 0, 0]
    elif severity == "severe":
        if urgency == "immediate" or urgency == "expected":  # red
            persistent_message = "!"
            recheck_seconds = 15
            return [255, 0, 0]
        else:
            persistent_message = "."
            recheck_seconds = 60
            return [255, 255, 0]  # yellow
    elif severity == "moderate":  # yellow
        persistent_message = "!"
        return [255, 255, 0]
    elif severity == "minor":  # white
        persistent_message = ""
        return [0, 255, 0]
    elif urgency == "immediate":  # red
        persistent_message = "!"
        recheck_seconds = 15
        return [255, 0, 0]
    return [255,255,255]


if __name__ == "__main__":
    print(f"Program started at: {datetime.datetime.now()}")
    sense = SenseHat()
    sense.low_light = True
    sense.rotation = 90
    sense.clear()
    main()


