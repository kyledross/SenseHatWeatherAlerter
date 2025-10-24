import logging
from enum import Enum
from Display.IDisplay import IDisplay

class DisplayType(Enum):
    ADAFRUIT_213_EINK = "adafruit_213_eink"
    SENSE_HAT = "sense_hat"
    SENSE_HAT_EMULATOR = "sense_hat_emulator"
    CONSOLE = "console"

class DisplayFactory:
    @staticmethod
    def create_display(display_type: DisplayType) -> IDisplay:
        if display_type == DisplayType.ADAFRUIT_213_EINK:
            from Display.Adafruit_213_eInk_Bonnet import Adafruit213eInkBonnet
            return Adafruit213eInkBonnet()
        elif display_type == DisplayType.SENSE_HAT:
            from Display.SenseHatDisplay import SenseHatDisplay
            return SenseHatDisplay()
        elif display_type == DisplayType.SENSE_HAT_EMULATOR:
            from Display.SenseHatEmulatorDisplay import SenseHatEmulatorDisplay
            return SenseHatEmulatorDisplay()
        elif display_type == DisplayType.CONSOLE:
            from Display.ConsoleDisplay import ConsoleDisplay
            return ConsoleDisplay()
        else:
            raise ValueError(f"Unsupported display type: {display_type}")

    @staticmethod
    def create_display_automatically() -> IDisplay:
        logger = logging.getLogger(__name__)
        try:
            display = DisplayFactory.create_display(DisplayType.SENSE_HAT)
            return display
        except Exception as e:
            logger.info(f"SenseHatDisplay not available: {e}")
        try:
            display = DisplayFactory.create_display(DisplayType.SENSE_HAT_EMULATOR)
            return display
        except Exception as e:
            logger.info(f"SenseHatEmulatorDisplay not available: {e}")
        try:
            display = DisplayFactory.create_display(DisplayType.ADAFRUIT_213_EINK)
            return display
        except Exception as e:
            logger.info(f"Adafruit213eInkBonnet not available: {e}")
        try:
            display = DisplayFactory.create_display(DisplayType.CONSOLE)
            return display
        except Exception as e:
            logger.error(f"Error creating ConsoleDisplay: {e}", exc_info=True)
            raise ValueError("No supported display found")
