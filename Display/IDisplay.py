from abc import ABC, abstractmethod
from typing import Callable, Optional

class IDisplay(ABC):
    @abstractmethod
    def display_message(self, title: str, message: str = "", detail: str = "", color=None):
        pass

    @abstractmethod
    def clear_display(self):
        pass

    @abstractmethod
    def heartbeat(self):
        pass

    def set_button_press_callback(self, callback: Optional[Callable[[], None]]):
        """Set callback to be called when a button is pressed on the display device.
        Default implementation does nothing - override in subclasses with button support."""
        pass
    
    @property
    def supports_long_message(self) -> bool:
        """Returns True if the display can show long scrolling messages."""
        return False
