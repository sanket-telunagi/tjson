import pyperclip


class ClipboardService:
    """Abstraction over system clipboard."""

    @staticmethod
    def copy(text: str) -> bool:
        try:
            pyperclip.copy(text)
            return True
        except Exception:
            # Log error here in a real app
            return False
