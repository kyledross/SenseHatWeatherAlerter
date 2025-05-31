from abc import ABC
from Display.IDisplay import IDisplay
from sense_hat import SenseHat

class SenseHatDisplay(IDisplay, ABC):
    sense:SenseHat = None
    def __init__(self):
        self.sense = SenseHat()
        self.sense.low_light = True
        self.sense.rotation = 90
        self.sense.clear()

    def display_message(self, title: str, message: str = "", detail: str = "", color=None):
        # The SenseHat, being a scrolling display, will only display the title.
        # It will then leave a full-stop on the display to let the user know that
        # there is an active alert.
        if color is None:
            color = [255, 255, 255]
        if title:
            self.sense.show_message(title, scroll_speed=0.05, text_colour=color)
            self.sense.show_letter(".", text_colour=color)
        else:
            self.sense.clear()
        pass

    def clear_display(self):
        self.sense.clear()

