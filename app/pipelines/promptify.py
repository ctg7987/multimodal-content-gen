"""Prompt engineering pipeline stub.

TODO: Improve system/user prompts and templates.
"""
from typing import Any, Dict


def promptify(input_data: Dict[str, Any]) -> str:
    title = input_data.get("title", "Untitled")
    return f"Prompt for: {title}"
