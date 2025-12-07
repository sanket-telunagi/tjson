import os

from textual.app import ComposeResult
from textual.screen import Screen
from textual.containers import Horizontal, Vertical
from textual.widgets import Header, Footer, Button, Switch, Label
from textual import on, work
from textual.timer import Timer

from tjson.ui.widgets.editor_pane import EditorPane
from tjson.core.processor import JSONProcessor, ProcessingResult
from tjson.services.clipboard import ClipboardService

# from tjson.ui.screens.file_prompt import FilePromptScreen
from tjson.ui.screens.file_picker import FilePickerScreen


class MainScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.debounce_timer: Timer | None = None

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)

        with Horizontal(id="main-container"):
            # --- LEFT PANE (INPUT) ---
            with Vertical(classes="pane-container"):
                yield EditorPane(title="INPUT (Raw)", id="input-pane", theme="dracula")

                with Horizontal(classes="action-bar"):
                    # Load File Button
                    yield Button("📂 Load File", id="load-btn", variant="primary")
                    # Paste Button
                    yield Button("📋 Paste", id="paste-btn", variant="default")

                # yield Button(
                #     "📋 Paste from Clipboard", id="paste-btn", variant="primary"
                # )
            # --- RIGHT PANE (OUTPUT) ---
            with Vertical(classes="pane-container"):
                yield EditorPane(
                    title="OUTPUT (Waiting...)",
                    id="output-pane",
                    read_only=True,
                    theme="monokai",
                )

                # --- ACTION BAR (Minify Switch + Copy Button) ---
                with Horizontal(classes="action-bar"):
                    # 1. Copy Button (Right - Fills remaining space)
                    yield Button("📋 Copy Output", id="copy-btn", variant="success")

                    # 2. Minify Controls (Left)
                    with Horizontal(classes="minify-group"):
                        yield Label("Minify", classes="minify-label")
                        yield Switch(value=False, id="minify-switch", animate=True)

        yield Footer()

    def on_mount(self) -> None:
        self.query_one("#input-pane").text_area.focus()

    # --- ACTION HANDLERS ---

    @on(Button.Pressed, "#paste-btn")
    def action_paste_from_clipboard(self) -> None:
        try:
            import pyperclip

            content = pyperclip.paste()
            if content:
                self.query_one("#input-pane", EditorPane).set_text(content)
                self.notify(f"Pasted {len(content)} characters", title="Success")
            else:
                self.notify("Clipboard is empty", severity="warning")
        except Exception as e:
            self.notify(f"Clipboard Error: {str(e)}", severity="error")

    @on(Button.Pressed, "#load-btn")
    def action_load_file(self) -> None:
        """Switch Input Pane to a File Input mode temporarily"""
        self.app.push_screen(FilePickerScreen(), callback=self.load_file_content)

    def load_file_content(self, file_path: str | None) -> None:
        """Callback when file path is entered"""
        if not file_path:
            return  # User cancelled

        if not os.path.exists(file_path):
            self.notify(f"File not found: {file_path}", severity="error")
            return

        try:
            # Check file size (Optional safety check)
            file_size_mb = os.path.getsize(file_path) / (1024 * 1024)
            if file_size_mb > 500:
                self.notify(
                    "Warning: Loading very large file (>500MB)", severity="warning"
                )

            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
                self.query_one("#input-pane", EditorPane).set_text(content)
                self.notify(f"Loaded {os.path.basename(file_path)}", title="Success")

        except UnicodeDecodeError:
            self.notify("Error: File is not valid text/JSON", severity="error")
        except Exception as e:
            self.notify(f"Error reading file: {str(e)}", severity="error")

    @on(EditorPane.Changed, "#input-pane")
    def on_input_changed(self, event: EditorPane.Changed) -> None:
        self.trigger_processing(event.value)

    @on(Switch.Changed, "#minify-switch")
    def on_minify_changed(self, event: Switch.Changed) -> None:
        # Re-process using current input when switch toggles
        current_input = self.query_one("#input-pane", EditorPane).get_text()
        self.trigger_processing(current_input)

    def trigger_processing(self, text: str) -> None:
        if self.debounce_timer:
            self.debounce_timer.stop()

        # Check toggle state
        is_minified = self.query_one("#minify-switch", Switch).value

        # Debounce
        self.debounce_timer = self.set_timer(
            0.6, lambda: self.process_json_background(text, is_minified)
        )

    @work(thread=True)
    def process_json_background(self, raw_text: str, minify: bool) -> None:
        self.app.call_from_thread(self.set_processing_state, True)
        result = JSONProcessor.process(raw_text, minify=minify)
        self.app.call_from_thread(self.update_ui_with_result, result)

    def set_processing_state(self, is_processing: bool) -> None:
        output_pane = self.query_one("#output-pane", EditorPane)
        label = output_pane.query_one(".pane-label")  # This targets the Static title

        if is_processing:
            label.update("OUTPUT (Processing... ⏳)")
            output_pane.add_class("processing")
        else:
            is_minified = self.query_one("#minify-switch", Switch).value
            title = "OUTPUT (Minified)" if is_minified else "OUTPUT (Pretty)"
            label.update(title)
            output_pane.remove_class("processing")

    def update_ui_with_result(self, result: ProcessingResult) -> None:
        output_pane = self.query_one("#output-pane", EditorPane)
        input_pane = self.query_one("#input-pane", EditorPane)

        self.set_processing_state(False)

        if result.is_valid:
            output_pane.set_text(result.formatted_text)
            input_pane.remove_class("error")
        else:
            input_pane.add_class("error")

    @on(Button.Pressed, "#copy-btn")
    def action_copy(self) -> None:
        text = self.query_one("#output-pane", EditorPane).get_text()
        if text:
            if ClipboardService.copy(text):
                self.notify("Copied to clipboard!", title="Success")
            else:
                self.notify("Clipboard Error", severity="error")
