import base64
import gzip
import io
import binascii
import re

def safe_b64decode(data: str) -> str:
    """
    Absolutely safe base64 decoder for LLM output.
    - Never throws
    - Handles missing padding
    - Handles non-base64 garbage
    - Handles gzip
    - Handles invalid UTF-8
    """

    if not isinstance(data, str) or not data.strip():
        return ""

    try:
        # Strip common wrappers
        data = data.strip()
        data = re.sub(r"^```.*?\n", "", data, flags=re.DOTALL)
        data = re.sub(r"\n```$", "", data)

        # Remove whitespace
        data = "".join(data.split())

        # Fix padding
        data += "=" * (-len(data) % 4)

        # Decode WITHOUT validation 
        raw = base64.b64decode(data, validate=False)

        # GZIP detection
        if raw[:2] == b"\x1f\x8b":
            try:
                return gzip.GzipFile(fileobj=io.BytesIO(raw)).read().decode(
                    "utf-8", errors="replace"
                )
            except Exception:
                pass

        return raw.decode("utf-8", errors="replace")

    except binascii.Error:
        return ""

    except Exception:
        return ""
