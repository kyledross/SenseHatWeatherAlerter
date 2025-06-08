from abc import ABC, abstractmethod

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