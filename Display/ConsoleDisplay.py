from Display.IDisplay import IDisplay


class ConsoleDisplay(IDisplay):
    def display_message(self, title: str, message: str = "", detail: str = "", color=None):
        print(title)
        print(message)
        pass
    def clear_display(self):
        pass
    def heartbeat(self):
        pass