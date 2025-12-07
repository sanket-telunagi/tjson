from textual.app import ComposeResult
from textual.screen import Screen
from textual.containers import Horizontal
from textual.widgets import Header, Footer, Button
from textual import on

from ui.widgets.editor_pane import EditorPane
from core.processor import JSONProcessor
from services.clipboard import ClipboardService


class MainScreen(Screen):
    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)

        with Horizontal(id="main-container"):
            yield EditorPane(title="INPUT (Raw)", id="input-pane")

            # The output pane needs a button, so we wrap it or handle it here
            with EditorPane(title="OUTPUT (Pretty)", id="output-pane", read_only=True):
                yield Button("📋 Copy Output", id="copy-btn")

        yield Footer()

    def on_mount(self) -> None:
        self.query_one("#input-pane-area").focus()

    @on(
        EditorPane.Changed
    )  # You might need to bubble the TextArea event up in EditorPane
    def on_input_changed(self) -> None:
        # Note: In real implementation, listen to specific TextArea changed event
        input_pane = self.query_one("#input-pane", EditorPane)
        output_pane = self.query_one("#output-pane", EditorPane)

        raw_text = input_pane.get_text()

        # Call Core Logic
        result = JSONProcessor.process(raw_text)

        if result.is_valid:
            output_pane.set_text(result.formatted_text)
            input_pane.remove_class("error")
        else:
            # We don't clear output on error, just mark red
            input_pane.add_class("error")

    @on(Button.Pressed, "#copy-btn")
    def action_copy(self) -> None:
        text = self.query_one("#output-pane", EditorPane).get_text()
        if text:
            if ClipboardService.copy(text):
                self.notify("Copied!", title="Success")
            else:
                self.notify("Clipboard error", severity="error")
