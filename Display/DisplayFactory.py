from enum import Enum
from Display.IDisplay import IDisplay
from Display.Adafruit_213_eInk_Bonnet import Adafruit213eInkBonnet


class DisplayType(Enum):
    ADAFRUIT_213_EINK = "adafruit_213_eink"


class DisplayFactory:
    @staticmethod
    def create_display(display_type: DisplayType) -> IDisplay:
        if display_type == DisplayType.ADAFRUIT_213_EINK:
            return Adafruit213eInkBonnet()
        else:
            raise ValueError(f"Unsupported display type: {display_type}")