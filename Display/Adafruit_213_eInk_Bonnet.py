from abc import ABC
import board
import busio
import digitalio
from adafruit_epd.epd import Adafruit_EPD

from Display.IDisplay import IDisplay

# SD1680 version, not 1680Z
class Adafruit213eInkBonnet(IDisplay, ABC):
    def __init__(self):

        spi = busio.SPI(board.SCK, MOSI=board.MOSI, MISO=board.MISO)
        ecs = digitalio.DigitalInOut(board.CE0)
        dc = digitalio.DigitalInOut(board.D22)
        rst = digitalio.DigitalInOut(board.D27)
        busy = digitalio.DigitalInOut(board.D17)
        srcs = None

        from adafruit_epd.ssd1680 import Adafruit_SSD1680
        self.display = Adafruit_SSD1680(122, 250, spi, cs_pin=ecs, dc_pin=dc, sramcs_pin=None,
                                        rst_pin=rst, busy_pin=busy)
        self.display.rotation = 3

    def detail(self, detail: str):
        pass

    def _wrap_text(self, text: str, width: int) -> list:
        words = text.split()
        lines = []
        current_line = []
        current_length = 0

        for word in words:
            word_length = len(word)
            if current_length + word_length + len(current_line) <= width:
                current_line.append(word)
                current_length += word_length
            else:
                lines.append(' '.join(current_line))
                current_line = [word]
                current_length = word_length

        if current_line:
            lines.append(' '.join(current_line))
        return lines

    def display_message(self, title: str, message: str = "", detail: str = "", color=None):
        self.clearScreen()
        self.display.text(title, 10, 10, Adafruit_EPD.BLACK, size=3)
        self.display.text(message, 10, 40, Adafruit_EPD.BLACK, size=2)
        # Calculate lines needed for detail text with word wrapping
        lines = self._wrap_text(detail, 40)
        for i, line in enumerate(lines):
            self.display.text(line, 10, 60 + (i * 10), Adafruit_EPD.BLACK, size=1)
        self.display.display()
        pass

    def clearScreen(self):
        self.display.fill(Adafruit_EPD.WHITE)
        pass