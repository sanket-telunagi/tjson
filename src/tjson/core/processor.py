import json
from dataclasses import dataclass
from typing import Optional, Tuple


@dataclass
class ProcessingResult:
    formatted_text: str
    is_valid: bool
    error_message: Optional[str] = None


class JSONProcessor:
    """Handles the business logic of parsing and formatting JSON."""

    @staticmethod
    def process(raw_text: str, indent: int = 4) -> ProcessingResult:
        if not raw_text.strip():
            return ProcessingResult("", True, None)

        try:
            parsed = json.loads(raw_text)
            formatted = json.dumps(parsed, indent=indent)
            return ProcessingResult(formatted, True, None)
        except json.JSONDecodeError as e:
            return ProcessingResult("", False, str(e))
