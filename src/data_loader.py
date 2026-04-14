from __future__ import annotations

from pathlib import Path
import requests

DATA_URL = "https://raw.githubusercontent.com/josephrmartinez/recipe-dataset/main/13k-recipes.csv"


def ensure_dataset(target_path: str | Path) -> Path:
    path = Path(target_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists() and path.stat().st_size > 1024:
        return path

    response = requests.get(DATA_URL, timeout=30)
    response.raise_for_status()
    path.write_bytes(response.content)
    return path
