from textual.app import ComposeResult
from textual.containers import Vertical
from textual.widgets import Label, TextArea, Static
from textual.widget import Widget
from textual.message import Message
from textual import on


class EditorPane(Widget):
    """A composite widget containing a label and a text editor."""

    class Changed(Message):
        control = None

        def __init__(self, editor_pane: Widget, value: str) -> None:
            self.value = value
            super().__init__()
            self.control = editor_pane

    def __init__(
        self, title: str, id: str, read_only: bool = False, theme: str = "dracula"
    ) -> None:
        super().__init__(id=id)
        self.title = title
        self.read_only = read_only
        self.theme = theme

    def compose(self) -> ComposeResult:
        with Vertical():
            yield Static(self.title, classes="pane-label")

            # --- ENABLE SYNTAX HIGHLIGHTING HERE ---
            ta = TextArea.code_editor(
                language="json",  # Tells it to look for JSON syntax
                theme=getattr(
                    self, "theme", "dracula"
                ),  # Adds the colors (try: 'monokai', 'github_dark'),
                # theme="cyberpunk",  # Custom theme defined in syntax_theme.py
                read_only=self.read_only,
            )
            # ---------------------------------------

            yield ta

    @property
    def text_area(self) -> TextArea:
        return self.query_one(TextArea)

    def get_text(self) -> str:
        return self.text_area.text

    def set_text(self, text: str) -> None:
        self.text_area.text = text

    @on(TextArea.Changed)
    def _on_internal_change(self, event: TextArea.Changed) -> None:
        event.stop()
        self.post_message(self.Changed(self, self.text_area.text))
