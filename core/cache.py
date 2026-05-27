import json
import os
from core.config import settings

CACHE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data", "cache.json")

def save_to_cache(data):
    with open(CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

def load_from_cache():
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []
