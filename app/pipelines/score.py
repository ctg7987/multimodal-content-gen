"""Content scoring stub.

TODO: Replace with actual model/heuristics.
"""
from typing import Any, Dict


def score_content(content: Dict[str, Any]) -> float:
    # Deterministic mock score
    copies = content.get("copies", [])
    imgs = content.get("images", [])
    return round(min(1.0, 0.5 + 0.05 * len(copies) + 0.02 * len(imgs)), 2)
