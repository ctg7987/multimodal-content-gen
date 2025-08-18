"""Basic config + in-memory JOBS store.

TODO: Load from environment variables via python-dotenv and os.environ
when we're ready to introduce real provider keys and DB config.
"""
from typing import Dict, Any

# Simple in-memory jobs store. Replace with Redis/DB later.
JOBS: Dict[str, Dict[str, Any]] = {}
