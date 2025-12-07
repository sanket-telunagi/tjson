from textual.app import ComposeResult
from textual.containers import Vertical
from textual.widgets import Label, TextArea
from textual.widget import Widget


class EditorPane(Widget):
    """A composite widget containing a label and a text editor."""

    def __init__(self, title: str, id: str, read_only: bool = False):
        super().__init__(id=id)
        self.title = title
        self.read_only = read_only

    def compose(self) -> ComposeResult:
        with Vertical():
            yield Label(self.title, classes="pane-label")
            ta = TextArea.code_editor(language="json", read_only=self.read_only)
            ta.id = f"{self.id}-area"  # internal ID for the TextArea
            yield ta

    @property
    def text_area(self) -> TextArea:
        return self.query_one(TextArea)

    def get_text(self) -> str:
        return self.text_area.text

    def set_text(self, text: str) -> None:
        self.text_area.text = text
