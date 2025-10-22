import logging
import threading
from time import sleep
from typing import Callable, Optional

from Display.IDisplay import IDisplay

class SenseHatDisplay(IDisplay):
    sense = None
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.sense_hat_found: bool = False
        self.button_callback: Optional[Callable[[], None]] = None
        self.button_monitor_thread: Optional[threading.Thread] = None
        self.stop_monitor = threading.Event()
        
        try:
            # noinspection PyUnresolvedReferences
            from sense_hat import SenseHat
            self.sense_hat_found = True
        except Exception as e:
            self.logger.debug(f"SenseHat hardware not found: {e}")
        if not self.sense_hat_found:
            try:
                # noinspection PyUnresolvedReferences
                from sense_emu import SenseHat
            except Exception:
                raise ValueError("No SenseHat or SenseHat Emu found")
        # noinspection PyUnboundLocalVariable
        self.sense = SenseHat()
        self.sense.low_light = True
        self.sense.rotation = 90
        self.sense.clear()

    def display_message(self, title: str, message: str = "", detail: str = "", color=None):
        # The SenseHat, being a scrolling display, will only display the title.
        # It will then leave a full-stop on the display to let the user know that
        # there is an active alert.
        show_full_stop = True
        if color is None:
            color = [255, 255, 255]
            show_full_stop = False
        if title:
            self.sense.show_message(". . . " + title, scroll_speed=0.05, text_colour=color)
            if show_full_stop:
                self.sense.show_letter(".", text_colour=color)
        else:
            self.sense.clear()

    def clear_display(self):
        self.sense.clear()


    def heartbeat(self):
        self.sense.set_pixel(7,7,0,255,0)
        sleep(.1)
        self.sense.set_pixel(7,7,0,0,0)

    def set_button_press_callback(self, callback: Optional[Callable[[], None]]):
        """Set callback to be called when the middle joystick button is pressed."""
        self.button_callback = callback
        if callback and not self.button_monitor_thread:
            self.button_monitor_thread = threading.Thread(target=self._monitor_joystick, daemon=True)
            self.button_monitor_thread.start()

    def _monitor_joystick(self):
        """Monitor the joystick middle button press in a background thread."""
        while not self.stop_monitor.is_set():
            try:
                for event in self.sense.stick.get_events():
                    if event.action == "pressed" and event.direction == "middle":
                        if self.button_callback:
                            self.button_callback()
                sleep(0.1)
            except Exception as e:
                self.logger.error(f"Error monitoring joystick: {e}", exc_info=True)
                sleep(1)
