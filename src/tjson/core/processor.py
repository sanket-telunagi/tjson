import orjson
from dataclasses import dataclass
from typing import Optional, Tuple


@dataclass
class ProcessingResult:
    formatted_text: str
    is_valid: bool
    error_message: Optional[str] = None


class JSONProcessor:
    @staticmethod
    def process(raw_text: str, indent: int = 4) -> ProcessingResult:
        if not raw_text.strip():
            return ProcessingResult("", True, None)

        try:
            # orjson.loads is 10x-50x faster than json.loads
            parsed = orjson.loads(raw_text)

            # orjson.dumps returns bytes, so we decode.
            # OPTION_INDENT_2 is closest to standard pretty print in orjson
            formatted = orjson.dumps(parsed, option=orjson.OPT_INDENT_2).decode("utf-8")

            return ProcessingResult(formatted, True, None)
        except orjson.JSONDecodeError as e:
            return ProcessingResult("", False, str(e))
