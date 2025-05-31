from abc import ABC, abstractmethod

class IDisplay(ABC):
    @abstractmethod
    def displayMessage(self, title: str, message: str, detail: str = ""):
        pass