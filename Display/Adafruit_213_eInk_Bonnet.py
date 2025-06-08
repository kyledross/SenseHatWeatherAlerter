from abc import ABC
import board
import busio
import digitalio
import os.path
from datetime import datetime
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
        current_dir = os.path.dirname(os.path.abspath(__file__))
        self.font_path = os.path.join(current_dir, 'font5x8.bin')

        from adafruit_epd.ssd1680 import Adafruit_SSD1680
        self.display = Adafruit_SSD1680(122, 250, spi, cs_pin=ecs, dc_pin=dc, sramcs_pin=None,
                                        rst_pin=rst, busy_pin=busy)
        self.display.rotation = 3
        self.heartbeat_count:int = 0
        self.display_is_clear:bool = False
        self.clear_display()

    @staticmethod
    def wrap_text(text: str, width: int) -> list:
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
        # self.display.text(title, 10, 10, Adafruit_EPD.BLACK, size=3, font_name=self.font_path)
        # Calculate lines needed for detail text with word wrapping
        if title:
            self.clear_display()
            lines = self.wrap_text(title, 13)
            for i, line in enumerate(lines):
                self.display.text(line, 3, 0 + (i * 24), Adafruit_EPD.BLACK, size=3, font_name=self.font_path)
            self.display.display()
            self.display_is_clear = False
        elif not title:
            self.clear_display()
        pass

    def clear_display(self):
        if self.display_is_clear:
            return
        self.display.fill(Adafruit_EPD.WHITE)
        self.display.display()
        self.display_is_clear = True
        pass
    
    def heartbeat(self):
        if self.heartbeat_count == 0:
            current_time = datetime.now().strftime("%Y-%m-%d %I:%M %p")
            self.display_message(f"Monitoring at {current_time}")
        self.heartbeat_count += 1
        if self.heartbeat_count >= 4:
            self.heartbeat_count = 0

