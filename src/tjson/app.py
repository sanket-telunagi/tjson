from textual.app import App
from ui.screens.main_screen import MainScreen
import os


class TJSONApp(App):
    CSS_PATH = os.path.join("ui", "styles", "main.tcss")

    def on_mount(self):
        self.push_screen(MainScreen())


def run():
    app = TJSONApp()
    app.run()
