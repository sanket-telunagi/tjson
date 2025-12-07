from textual.app import ComposeResult
from textual.screen import Screen
from textual.containers import Horizontal, Vertical
from textual.widgets import Header, Footer, Button
from textual import on, work
from textual.timer import Timer

from tjson.ui.widgets.editor_pane import EditorPane
from tjson.core.processor import JSONProcessor, ProcessingResult
from tjson.services.clipboard import ClipboardService


class MainScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.debounce_timer: Timer | None = None

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)

        with Horizontal(id="main-container"):
            # LEFT PANE: Input
            with Vertical(classes="pane-container"):  # Added container for layout
                yield EditorPane(title="INPUT (Raw)", id="input-pane", theme="dracula")
                # NEW: Paste Button
                yield Button(
                    "📋 Paste from Clipboard", id="paste-btn", variant="primary"
                )

            # RIGHT PANE: Output
            with Vertical(classes="pane-container"):
                yield EditorPane(
                    title="OUTPUT (Waiting...)",
                    id="output-pane",
                    read_only=True,
                    theme="monokai",
                )
                yield Button("📋 Copy Output", id="copy-btn", variant="success")

        yield Footer()

    def on_mount(self) -> None:
        self.query_one("#input-pane").text_area.focus()

    # --- NEW PASTE HANDLER ---
    @on(Button.Pressed, "#paste-btn")
    def action_paste_from_clipboard(self) -> None:
        """Bypasses terminal input limits by reading OS clipboard directly."""
        try:
            import pyperclip

            content = pyperclip.paste()
            if not content:
                self.notify("Clipboard is empty!", title="Warning", severity="warning")
                return

            # Set text directly. This triggers the 'Changed' event automatically
            self.query_one("#input-pane", EditorPane).set_text(content)
            self.notify(f"Pasted {len(content)} characters!", title="Success")

        except Exception as e:
            self.notify(f"Clipboard Error: {str(e)}", title="Error", severity="error")

    # --- EXISTING LOGIC ---
    @on(EditorPane.Changed, "#input-pane")
    def on_input_changed(self, event: EditorPane.Changed) -> None:
        if self.debounce_timer:
            self.debounce_timer.stop()

        text_snapshot = event.value
        # Debounce for 0.6s
        self.debounce_timer = self.set_timer(
            0.6, lambda: self.process_json_background(text_snapshot)
        )

    @work(thread=True)
    def process_json_background(self, raw_text: str) -> None:
        self.app.call_from_thread(self.set_processing_state, True)
        result = JSONProcessor.process(raw_text)
        self.app.call_from_thread(self.update_ui_with_result, result)

    def set_processing_state(self, is_processing: bool) -> None:
        output_pane = self.query_one("#output-pane", EditorPane)
        if is_processing:
            output_pane.border_title = "OUTPUT (Processing... ⏳)"
            output_pane.styles.border = ("solid", "#e6b400")
        else:
            output_pane.border_title = "OUTPUT (Pretty)"

    @on(Button.Pressed, "#copy-btn")
    def action_copy(self) -> None:
        text = self.query_one("#output-pane", EditorPane).get_text()
        if text:
            if ClipboardService.copy(text):
                self.notify("Copied to clipboard!", title="Success")
            else:
                self.notify("Failed to access clipboard", severity="error")

    def set_processing_state(self, is_processing: bool) -> None:
        output_pane = self.query_one("#output-pane", EditorPane)

        if is_processing:
            # Change Title
            output_pane.query_one(".pane-label").update("OUTPUT (Processing... ⏳)")
            # Add CSS class for styling (defined in main.tcss)
            output_pane.add_class("processing")
        else:
            output_pane.query_one(".pane-label").update("OUTPUT (Pretty)")
            output_pane.remove_class("processing")

    def update_ui_with_result(self, result: ProcessingResult) -> None:
        output_pane = self.query_one("#output-pane", EditorPane)
        input_pane = self.query_one("#input-pane", EditorPane)

        self.set_processing_state(False)

        if result.is_valid:
            output_pane.set_text(result.formatted_text)
            input_pane.remove_class("error")
            # We let the default CSS take over (purple focus or grey idle)
        else:
            input_pane.add_class("error")
            # Optional: Display error in status bar or notification
            self.notify(f"Invalid JSON: {result.error_message}", severity="error")
