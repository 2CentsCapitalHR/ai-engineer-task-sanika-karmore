# utils.py
import json
import os
from typing import List

def save_json(obj, path):
    with open(path, "w", encoding="utf8") as f:
        json.dump(obj, f, indent=2, ensure_ascii=False)

def ensure_dir(path):
    os.makedirs(path, exist_ok=True)
