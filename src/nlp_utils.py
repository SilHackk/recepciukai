from __future__ import annotations

import ast
import re
import unicodedata
from dataclasses import dataclass
from typing import Iterable, List, Optional

TOKEN_RE = re.compile(r"[a-zA-Z\u00C0-\u017F]+")
QUANTITY_RE = re.compile(
    r"(?P<amount>\d+(?:[\.,]\d+)?)\s*(?P<unit>kg|g|mg|l|ml|tbsp|tsp|cup|cups|pcs|pc|vnt|saukst|šaukšt|saukstel|šaukštel)?",
    re.IGNORECASE,
)

UNIT_NORMALIZATION = {
    "l": "ml",
    "ml": "ml",
    "kg": "g",
    "g": "g",
    "mg": "mg",
    "tbsp": "tbsp",
    "tsp": "tsp",
    "cup": "cup",
    "cups": "cup",
    "pcs": "pcs",
    "pc": "pcs",
    "vnt": "pcs",
    "saukst": "tbsp",
    "šaukšt": "tbsp",
    "saukstel": "tsp",
    "šaukštel": "tsp",
}

LT_TO_EN = {
    "kiausinis": "egg",
    "kiausiniai": "egg",
    "kiaušiniai": "egg",
    "kiaus": "egg",
    "miltai": "flour",
    "kvietiniai miltai": "flour",
    "pienas": "milk",
    "vanduo": "water",
    "cukrus": "sugar",
    "druska": "salt",
    "pipirai": "pepper",
    "juodieji pipirai": "black pepper",
    "sviestas": "butter",
    "aliejus": "oil",
    "alyvuogių aliejus": "olive oil",
    "svogunas": "onion",
    "svogūnas": "onion",
    "svogunai": "onion",
    "svogūnai": "onion",
    "cesnakas": "garlic",
    "česnakas": "garlic",
    "pomidoras": "tomato",
    "pomidorai": "tomato",
    "bulves": "potato",
    "bulvės": "potato",
    "vistiena": "chicken",
    "vištiena": "chicken",
    "ryziai": "rice",
    "ryžiai": "rice",
    "makaronai": "pasta",
    "suris": "cheese",
    "sūris": "cheese",
    "grietine": "sour cream",
    "grietinė": "sour cream",
    "jautiena": "beef",
    "kiauliena": "pork",
    "morka": "carrot",
    "morkos": "carrot",
    "agurkas": "cucumber",
    "agurkai": "cucumber",
    "duona": "bread",
    "medus": "honey",
    "bananas": "banana",
    "obuoliai": "apple",
}

STOPWORDS = {
    "fresh", "ground", "small", "large", "extra", "virgin", "chopped", "sliced",
    "diced", "minced", "optional", "to", "taste", "and", "for", "of", "the",
    "a", "an", "or", "with", "red", "green", "yellow", "white", "black",
}


@dataclass
class PantryItem:
    original: str
    name: str
    amount: Optional[float]
    unit: Optional[str]


def strip_accents(text: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFKD", text) if not unicodedata.combining(c))


def normalize_text(text: str) -> str:
    text = strip_accents(text.lower()).strip()
    text = re.sub(r"\s+", " ", text)
    return text


def normalize_ingredient_name(text: str) -> str:
    text = normalize_text(text)
    text = re.sub(r"[^a-z\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    text = LT_TO_EN.get(text, text)
    tokens = [tok for tok in TOKEN_RE.findall(text) if tok not in STOPWORDS]
    if not tokens:
        return text
    return " ".join(tokens[:3])


def parse_quantity(text: str) -> tuple[Optional[float], Optional[str]]:
    match = QUANTITY_RE.search(normalize_text(text).replace(",", "."))
    if not match:
        return None, None
    amount = float(match.group("amount"))
    unit = match.group("unit")
    if not unit:
        return amount, None
    unit = UNIT_NORMALIZATION.get(unit.lower(), unit.lower())
    if unit == "g" and amount < 10:
        return amount, unit
    if unit == "kg":
        return amount * 1000.0, "g"
    if unit == "l":
        return amount * 1000.0, "ml"
    return amount, unit


def parse_pantry_lines(text: str) -> List[PantryItem]:
    items: List[PantryItem] = []
    for raw_line in text.splitlines():
        line = raw_line.strip(" -•\t")
        if not line:
            continue
        amount, unit = parse_quantity(line)
        cleaned = QUANTITY_RE.sub(" ", normalize_text(line), count=1).strip()
        cleaned = re.sub(r"\b(x|vnt|pcs|pc)\b", " ", cleaned).strip()
        name = normalize_ingredient_name(cleaned)
        items.append(PantryItem(original=line, name=name, amount=amount, unit=unit))
    return items


def ingredient_list_from_cell(value: str | list | None) -> List[str]:
    if value is None:
        return []
    if isinstance(value, list):
        raw = value
    else:
        text = str(value)
        try:
            parsed = ast.literal_eval(text)
            raw = parsed if isinstance(parsed, list) else [text]
        except Exception:
            raw = re.split(r"[,;|]", text)
    cleaned = []
    for item in raw:
        norm = normalize_ingredient_name(str(item))
        if norm:
            cleaned.append(norm)
    return cleaned


def tokenize_for_tfidf(items: Iterable[str]) -> str:
    return " ".join(normalize_ingredient_name(x) for x in items if normalize_ingredient_name(x))
