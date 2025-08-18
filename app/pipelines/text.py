"""Text generation pipeline stub.

TODO: Swap with OpenAI/other LLM provider.
"""
from typing import Any, Dict


def generate_text(input_data: Dict[str, Any]) -> str:
    channel = input_data.get("channel", "general")
    title = input_data.get("title", "Your Campaign")
    brief = input_data.get("brief", "")
    return f"Generated copy for {channel}: {title} — {brief}"
