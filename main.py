import datetime
from time import sleep
import os.path
import requests
from dataclasses import dataclass
from typing import Optional
from Display.DisplayFactory import DisplayFactory, DisplayType
from Display.IDisplay import IDisplay

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


class Alerter:
    recheck_seconds:int = 300  # 5 minutes
    persistent_message:str = ""
    first_api_request:bool = True
    display:IDisplay = None
    api_url:str = ""

    def __init__(self, url: str, display: IDisplay):
        self.display: IDisplay = display
        self.api_url: str = url

    def run(self):
        next_check: datetime = datetime.datetime.now()
        while True:
            while datetime.datetime.now() <= next_check:
                sleep(5)
            self.process_alerts()
            next_check = datetime.datetime.now() + datetime.timedelta(seconds=self.recheck_seconds)


    def process_alerts(self):
        weather_alert = self.get_weather_alert()
        self.display.clear_display()
        if weather_alert:
            if weather_alert.event:
                alert_color = self.get_alert_color(weather_alert.severity, weather_alert.urgency)
                self.display.display_message(title=weather_alert.event, color=alert_color)
            else:
                pass

    def get_weather_alert(self) -> Optional[WeatherAlert]:
        try:
            if self.first_api_request:
                self.display.display_message("Connecting...")
            response = requests.get(self.api_url)
            response.raise_for_status()
            if self.first_api_request:
                self.display.display_message("Connected")
                self.first_api_request = False
            data = response.json()
            return WeatherAlert(**data)
        except (requests.RequestException, ValueError) as e:
            print(f"Error fetching weather alert: {e}")
            self.recheck_seconds = 30
            return None


    def get_alert_color(self,severity, urgency):
        self.recheck_seconds = 300 # five minutes
        severity = severity.lower()
        urgency = urgency.lower()
        if severity == "extreme":  # red
            self.recheck_seconds = 15
            return [255, 0, 0]
        elif severity == "severe":
            if urgency == "immediate" or urgency == "expected":  # red
                self.recheck_seconds = 15
                return [255, 0, 0]
            else:
                self.recheck_seconds = 60
                return [255, 255, 0]  # yellow
        elif severity == "moderate":  # yellow
            return [255, 255, 0]
        elif severity == "minor":  # white
            return [0, 255, 0]
        elif urgency == "immediate":  # red
            self.recheck_seconds = 15
            return [255, 0, 0]
        return [255,255,255]


if __name__ == "__main__":
    config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config.txt')
    with open(config_path, 'r') as file:
        state, city, display_type = file.read().strip().split('\n')
    alerter = Alerter(f"http://rpi02w.local:8080/weather-alert/{state}/{city}",
                      DisplayFactory.create_display(DisplayType(display_type)))
    alerter.run()



