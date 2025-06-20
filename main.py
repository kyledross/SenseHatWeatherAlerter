import datetime
import os.path
import threading
from dataclasses import dataclass
from time import sleep
from typing import Optional

import requests

from Display.DisplayFactory import DisplayFactory
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

    def is_storm_active(self) -> bool:
        if self.last_storm_callback is None:
            return False
        time_diff = datetime.datetime.now() - self.last_storm_callback
        return time_diff.total_seconds() < (self.local_storm_time_to_live_minutes * 60)

    last_storm_callback: datetime.datetime = None
    local_storm_time_to_live_minutes: int = 30

    def __init__(self, display: IDisplay):
        self.display: IDisplay = display
        self.state:str = ""
        self.city:str = ""
        self.weather_box_server: str = ""
        self.last_config: str = ""
        self.storm_detector = None

    def run(self):
        self._start_storm_detector()      
        next_check: datetime = datetime.datetime.now()
        while True:
            while datetime.datetime.now() <= next_check:
                self.display.heartbeat()
                sleep(15)

            config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config.txt')
            with open(config_path, 'r') as file:
                read = file.read()
                self.weather_box_server, self.state, self.city = read.strip().split('\n')
                if read != self.last_config:
                    self.display.display_message(f"Monitoring {self.city}, {self.state}")
                    self.display.clear_display()
                    self.last_config = read
                self.api_url = f"{self.weather_box_server}/weather-alert/{self.state}/{self.city}"
                file.close()
            self.process_alerts()
            next_check = datetime.datetime.now() + datetime.timedelta(seconds=self.recheck_seconds)


    def process_alerts(self):
        weather_alert = self.get_weather_alert()
        if weather_alert or self.is_storm_active():
            alert_title = ""
            alert_color = [255, 255, 255]
            if weather_alert:
                alert_color = self.get_alert_color(weather_alert.severity, weather_alert.urgency)
            if self.is_storm_active() and alert_color != [255, 0, 0]:
                # a local storm has been detected, and there is not a current warning from the national weather service
                # so preempt any nws message and alert about the detected storm, instead
                alert_title = "Nearby Storm Detected"
                alert_color = [255, 0, 255]
                self.recheck_seconds = 60
            elif weather_alert.event:
                alert_title = weather_alert.event
            else:
                pass
            self.display.display_message(title=alert_title, color=alert_color)

    def get_weather_alert(self) -> Optional[WeatherAlert]:
        try:
            if self.first_api_request:
                self.display.display_message("Connecting")
            response = requests.get(self.api_url)
            response.raise_for_status()
            if self.first_api_request:
                self.display.display_message("Connected")
                self.first_api_request = False
            data = response.json()
            return WeatherAlert(**data)
        except (requests.RequestException, ValueError) as e:
            print(f"Error fetching weather alert: {e}")
            self.display.display_message("Error getting weather data. Retrying in 30 seconds.")
            self.recheck_seconds = 30
            return None


    def storm_detected_callback(self):
        self.last_storm_callback = datetime.datetime.now()

    def _start_storm_detector(self):
        from Detection.StormDetector import StormDetector
        self.storm_detector = StormDetector(storm_detected_callback=self.storm_detected_callback)
        if self.storm_detector.sense_hat_present():
            detector_thread = threading.Thread(target=self.storm_detector.run, daemon=True)
            detector_thread.start()


    def get_alert_color(self,severity, urgency):
            if severity is None or urgency is None:
                return [255,255,255]
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
    display = DisplayFactory.create_display_automatically()
    try:
        alerter = Alerter(display)
        alerter.run()
    except Exception as e:
        display.display_message(str(e))
        raise
