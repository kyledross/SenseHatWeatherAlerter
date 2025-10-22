import datetime
import logging
import os.path
import sys
import threading
import traceback
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
    check_now_event: threading.Event = None
    on_demand_check_requested: bool = False

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
        self.check_now_event = threading.Event()
        self.on_demand_check_requested = False
        self.display.set_button_press_callback(self._on_button_pressed)
        self.logger = logging.getLogger(__name__)

    def run(self):
        self._start_storm_detector()      
        next_check: datetime = datetime.datetime.now()
        while True:
            while datetime.datetime.now() <= next_check:
                if self.check_now_event.wait(timeout=15):
                    self.check_now_event.clear()
                    self.display.display_message("Checking")
                    break
                self.display.heartbeat()

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
            elif weather_alert and weather_alert.event:
                alert_title = weather_alert.event
            else:
                pass
            self.display.display_message(title=alert_title, color=alert_color)
            self.on_demand_check_requested = False
        else:
            # No valid weather alert and no storm active
            if self.on_demand_check_requested:
                self.display.display_message("No updates")
                self.on_demand_check_requested = False
            else:
                self.display.clear_display()

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
            
            # Ignore alerts with "UNKNOWN" severity
            if (data.get('severity') or '').upper() == 'UNKNOWN':
                self.logger.info(f"Ignoring alert with UNKNOWN severity: {data.get('event', 'N/A')}")
                return None
                
            return WeatherAlert(**data)
        except (requests.RequestException, ValueError) as e:
            self.logger.error(f"Error fetching weather alert: {e}", exc_info=True)
            self.display.display_message("Error getting weather data. Retrying in 30 seconds.")
            self.recheck_seconds = 30
            return None


    def storm_detected_callback(self, message: str):
        self.last_storm_callback = datetime.datetime.now()

    def _on_button_pressed(self):
        """Callback for when the display button is pressed."""
        self.on_demand_check_requested = True
        self.check_now_event.set()

    def _start_storm_detector(self):
        from Detection.StormDetector import StormDetector
        self.storm_detector = StormDetector(storm_detected_callback=self.storm_detected_callback)
        if self.storm_detector.sense_hat_present():
            detector_thread = threading.Thread(target=self._run_storm_detector_with_logging, daemon=True)
            detector_thread.start()

    def _run_storm_detector_with_logging(self):
        """Wrapper to catch and log storm detector thread exceptions."""
        try:
            self.storm_detector.run()
        except Exception as e:
            self.logger.critical(f"Storm detector thread crashed: {e}", exc_info=True)
            self.display.display_message("Storm detector error")


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


def setup_logging():
    """Configure logging to file and console."""
    log_dir = os.path.dirname(os.path.abspath(__file__))
    log_file = os.path.join(log_dir, 'weather_alerter.log')
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file, mode='a'),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    logger = logging.getLogger(__name__)
    logger.info("="*60)
    logger.info("Weather Alerter starting")
    return logger


if __name__ == "__main__":
    logger = setup_logging()
    display = None
    
    try:
        display = DisplayFactory.create_display_automatically()
        logger.info(f"Display initialized: {type(display).__name__}")
        
        alerter = Alerter(display)
        alerter.run()
    except KeyboardInterrupt:
        logger.info("Shutdown requested by user")
    except Exception as e:
        logger.critical(f"Fatal error: {e}", exc_info=True)
        if display:
            display.display_message("Fatal error - check logs")
        sys.exit(1)
