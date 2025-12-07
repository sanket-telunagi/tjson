from textual.app import App
from textual.widgets import TextArea
from tjson.ui.screens.main_screen import MainScreen
from tjson.ui.styles.syntax_theme import CYBERPUNK_THEME
import os


class TJSONApp(App):
    CSS_PATH = os.path.join("ui", "styles", "main.tcss")

    def on_mount(self):
        # 1. Register the custom theme with the global TextArea registry

        # TextArea.register_theme(CYBERPUNK_THEME)
        self.push_screen(MainScreen())


def run():
    # print(f"Available Languages: {TextArea.available_languages}")
    # print(f"Available Themes: {TextArea.available_themes}")
    app = TJSONApp()
    app.run()


run()
