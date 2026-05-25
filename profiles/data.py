# Load the signs dataset from disk

import json 
from pathlib import Path

_DATA_PATH = Path(__file__).parent / "signs.json"


def _load_signs():
    with open(_DATA_PATH, "r", encoding = 'utf-8') as f:
        return json.load(f)
    
SIGNS_DATA = _load_signs()
