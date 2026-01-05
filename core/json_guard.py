import json

class JSONRepairError(Exception):
    pass


def extract_balanced_json(text: str) -> str:
    """
    Extracts the first balanced JSON object from text.
    Handles nested braces safely.
    """
    start = text.find("{")
    if start == -1:
        raise JSONRepairError("No JSON object start found")

    depth = 0
    for i in range(start, len(text)):
        if text[i] == "{":
            depth += 1
        elif text[i] == "}":
            depth -= 1
            if depth == 0:
                return text[start:i + 1]

    raise JSONRepairError("Unbalanced JSON braces")


def safe_parse_json(text: str) -> dict:
    """
    Attempts strict parse, then repair-based parse.
    """
    if isinstance(text, dict):
        return text

    try:
        return json.loads(text)
    except Exception:
        repaired = extract_balanced_json(text)
        return json.loads(repaired)
