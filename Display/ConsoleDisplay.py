from Display.IDisplay import IDisplay


class ConsoleDisplay(IDisplay):
    def display_message(self, title: str, message: str = "", detail: str = "", color=None):
        print(title)
        print(message)

    def clear_display(self):
        pass

    def heartbeat(self):
        pass

    @property
    def supports_long_message(self) -> bool:
        """Console can display arbitrarily long messages."""
        return True
