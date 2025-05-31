from enum import Enum
from Display.IDisplay import IDisplay

class DisplayType(Enum):
    ADAFRUIT_213_EINK = "adafruit_213_eink"
    SENSE_HAT = "sense_hat"

class DisplayFactory:
    @staticmethod
    def create_display(display_type: DisplayType) -> IDisplay:
        if display_type == DisplayType.ADAFRUIT_213_EINK:
            from Display.Adafruit_213_eInk_Bonnet import Adafruit213eInkBonnet
            return Adafruit213eInkBonnet()
        elif display_type == DisplayType.SENSE_HAT:
            from Display.SenseHatDisplay import SenseHatDisplay
            return SenseHatDisplay()
        else:
            raise ValueError(f"Unsupported display type: {display_type}")

    @staticmethod
    def create_display_automatically() -> IDisplay:
        try:
            display = DisplayFactory.create_display(DisplayType.SENSE_HAT)
            return display
        except OSError:
            pass
        try:
            display = DisplayFactory.create_display(DisplayType.ADAFRUIT_213_EINK)
            return display
        except OSError:
            raise ValueError("No supported display found")
