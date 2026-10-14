import json
from pathlib import Path

REFERENCE_FILE = Path(__file__).with_name("engineering_reference.json")


def search_references(query: str) -> str:
    """Search the local engineering reference JSON file."""
    if not REFERENCE_FILE.exists():
        return "Engineering reference file was not found."

    try:
        with REFERENCE_FILE.open("r", encoding="utf-8") as file:
            data = json.load(file)

        words = query.lower().split()
        matches = []

        def search_items(item, path=""):
            if isinstance(item, dict):
                for key, value in item.items():
                    search_items(value, f"{path} {key}")
            elif isinstance(item, list):
                for value in item:
                    search_items(value, path)
            else:
                text = f"{path} {item}"
                score = sum(word in text.lower() for word in words)
                if score:
                    matches.append((score, text))

        search_items(data)
        matches.sort(key=lambda item: item[0], reverse=True)

        if not matches:
            return "No matching engineering reference was found."

        return "\n".join(text for _, text in matches[:5])

    except (OSError, json.JSONDecodeError) as error:
        return f"Could not read engineering references: {error}"
