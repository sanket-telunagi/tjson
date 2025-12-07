import orjson
from dataclasses import dataclass
from typing import Optional


@dataclass
class ProcessingResult:
    formatted_text: str
    is_valid: bool
    error_message: Optional[str] = None


class JSONProcessor:
    """
    High-performance JSON processing using Rust-based 'orjson'.
    """

    @staticmethod
    def process(raw_text: str, minify: bool = False) -> ProcessingResult:
        """
        Parses and formats JSON.

        Args:
            raw_text: The input JSON string.
            minify: If True, removes all whitespace. If False, pretty prints (2-space indent).
        """
        if not raw_text.strip():
            return ProcessingResult("", True, None)

        try:
            # 1. Parse (High speed)
            parsed = orjson.loads(raw_text)

            # 2. Format
            if minify:
                # orjson.dumps defaults to minified (no whitespace) - extremely fast
                bytes_output = orjson.dumps(parsed)
            else:
                # orjson supports 2-space indentation via options
                # Note: orjson is strict about 2 spaces for speed.
                # It does not support arbitrary 4-space indentation.
                bytes_output = orjson.dumps(parsed, option=orjson.OPT_INDENT_2)

            # 3. Decode bytes back to string for the UI
            formatted = bytes_output.decode("utf-8")

            return ProcessingResult(formatted, True, None)

        except orjson.JSONDecodeError as e:
            # Handle error (e.g., "line 1 column 5")
            return ProcessingResult("", False, str(e))
        except Exception as e:
            # Catch generic errors
            return ProcessingResult("", False, f"Unexpected error: {str(e)}")
