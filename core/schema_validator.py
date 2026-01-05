import json

class SchemaError(Exception):
    pass


def validate_json(data, required_keys: list[str]) -> dict:
    """
    Validates that required keys exist in parsed JSON.
    Accepts either str (raw JSON) or dict (parsed JSON).
    """
    if isinstance(data, str):
        try:
            data = json.loads(data)
        except Exception as exc:
            raise SchemaError("Invalid JSON format") from exc

    if not isinstance(data, dict):
        raise SchemaError("JSON must be an object")

    for key in required_keys:
        if key not in data:
            raise SchemaError(f"Missing required key: {key}")

    return data
