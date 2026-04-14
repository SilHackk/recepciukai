from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import List

import pandas as pd
from rapidfuzz import fuzz
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from .nlp_utils import PantryItem, ingredient_list_from_cell, tokenize_for_tfidf


@dataclass
class RecipeSuggestion:
    title: str
    ingredients: list[str]
    instructions: str
    similarity: float
    coverage: float
    missing: list[str]
    matched: list[str]


class RecipeEngine:
    def __init__(self, csv_path: str | Path):
        self.csv_path = Path(csv_path)
        self.df = self._load_dataset(self.csv_path)
        self.vectorizer = TfidfVectorizer(ngram_range=(1, 2), min_df=2)
        self.matrix = self.vectorizer.fit_transform(self.df["ingredient_text"])

    def _load_dataset(self, path: Path) -> pd.DataFrame:
        df = pd.read_csv(path)
        cols = {c.lower(): c for c in df.columns}
        title_col = cols.get("title") or cols.get("name")
        ing_col = cols.get("ingredients")
        instr_col = cols.get("instructions") or cols.get("directions")
        if not (title_col and ing_col and instr_col):
            raise ValueError("Dataset'e turi būti title, ingredients ir instructions stulpeliai.")
        out = df[[title_col, ing_col, instr_col]].copy()
        out.columns = ["title", "ingredients_raw", "instructions"]
        out = out.dropna().head(6000)
        out["ingredients"] = out["ingredients_raw"].apply(ingredient_list_from_cell)
        out = out[out["ingredients"].map(len) >= 3].copy()
        out["ingredient_text"] = out["ingredients"].apply(tokenize_for_tfidf)
        out["instructions"] = out["instructions"].astype(str)
        out["title"] = out["title"].astype(str)
        out = out.drop_duplicates(subset=["title", "ingredient_text"]).reset_index(drop=True)
        return out

    def _best_matches(self, pantry_tokens: set[str], recipe_tokens: list[str]) -> tuple[list[str], list[str]]:
        matched, missing = [], []
        for token in recipe_tokens:
            best = max((fuzz.ratio(token, p) for p in pantry_tokens), default=0)
            if token in pantry_tokens or best >= 88:
                matched.append(token)
            else:
                missing.append(token)
        return matched, missing

    def suggest(self, pantry_items: List[PantryItem], top_k: int = 5, max_missing: int = 3) -> List[RecipeSuggestion]:
        pantry_tokens = {item.name for item in pantry_items if item.name}
        pantry_text = " ".join(sorted(pantry_tokens))
        if not pantry_text:
            return []
        q = self.vectorizer.transform([pantry_text])
        sims = cosine_similarity(q, self.matrix).flatten()
        candidate_idx = sims.argsort()[::-1][: top_k * 15]

        suggestions: list[RecipeSuggestion] = []
        for idx in candidate_idx:
            row = self.df.iloc[idx]
            matched, missing = self._best_matches(pantry_tokens, row["ingredients"])
            coverage = len(matched) / max(len(row["ingredients"]), 1)
            if len(missing) > max_missing:
                continue
            suggestions.append(
                RecipeSuggestion(
                    title=row["title"],
                    ingredients=row["ingredients"],
                    instructions=row["instructions"],
                    similarity=float(sims[idx]),
                    coverage=float(coverage),
                    missing=missing[:max_missing],
                    matched=matched,
                )
            )
        suggestions.sort(key=lambda x: (x.coverage, x.similarity), reverse=True)
        unique = []
        seen = set()
        for s in suggestions:
            key = s.title.lower().strip()
            if key in seen:
                continue
            unique.append(s)
            seen.add(key)
            if len(unique) >= top_k:
                break
        return unique
