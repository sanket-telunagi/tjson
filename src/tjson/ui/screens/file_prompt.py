from textual.screen import ModalScreen
from textual.containers import Grid
from textual.widgets import Input, Label, Button
from textual.app import ComposeResult
from textual import on


class FilePromptScreen(ModalScreen[str]):
    """A modal dialog to ask for a filepath."""

    CSS = """
    FilePromptScreen {
        align: center middle;
        background: rgba(0,0,0,0.7);
    }
    
    #dialog {
        grid-size: 2;
        grid-gutter: 1;
        grid-rows: 1fr 3;
        padding: 1 2;
        width: 60;
        height: 14;
        background: #44475a; /* Dracula surface */
        border: round #bd93f9; /* Dracula Purple */
    }
    
    #question {
        column-span: 2;
        height: 1fr;
        content-align: center middle;
        text-style: bold;
    }
    
    Input {
        column-span: 2;
        margin-bottom: 1;
    }
    
    Button {
        width: 100%;
    }
    """

    def compose(self) -> ComposeResult:
        with Grid(id="dialog"):
            yield Label("Enter file path (e.g., data.json):", id="question")
            yield Input(placeholder="/path/to/file.json", id="path-input")
            yield Button("Cancel", variant="error", id="cancel")
            yield Button("Load", variant="success", id="load")

    def on_mount(self) -> None:
        self.query_one(Input).focus()

    @on(Button.Pressed, "#load")
    def on_load(self) -> None:
        path = self.query_one(Input).value
        self.dismiss(path)

    @on(Input.Submitted)
    def on_submit(self, event: Input.Submitted) -> None:
        self.dismiss(event.value)

    @on(Button.Pressed, "#cancel")
    def on_cancel(self) -> None:
        self.dismiss(None)
