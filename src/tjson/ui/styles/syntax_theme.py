from textual.widgets.text_area import TextAreaTheme
from rich.style import Style

# A custom theme designed for JSON
CYBERPUNK_THEME = TextAreaTheme(
    name="cyberpunk",
    base_style=Style(color="#e0e0e0", bgcolor="#1a1b26"),
    gutter_style=Style(color="#565f89", bgcolor="#16161e"),
    cursor_style=Style(color="#1a1b26", bgcolor="#c0caf5"),
    selection_style=Style(bgcolor="#33467c"),
    syntax_styles={
        # JSON Specifics
        "string": Style(color="#9ece6a"),  # Values (Green)
        "string.label": Style(
            color="#7aa2f7", italic=True, bold=True
        ),  # Keys (Blue + Italic)
        # Primitives
        "number": Style(color="#ff9e64"),  # Numbers (Orange)
        "boolean": Style(color="#bb9af7", bold=True),  # True/False (Purple + Bold)
        "null": Style(color="#565f89", italic=True),  # Null (Grey + Italic)
        # Structure
        "punctuation": Style(color="#89ddff"),  # Brackets (Cyan)
        "punctuation.delimiter": Style(color="#89ddff"),  # Colons/Commas
    },
)
