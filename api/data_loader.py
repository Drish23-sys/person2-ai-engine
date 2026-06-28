"""
data_loader.py
Loads careers.json once and provides helper functions to access it.
This is what connects your AI logic to Person 4's dataset.
"""

import json
import os

DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "careers.json")

_careers_cache = None


def load_careers() -> list:
    """Loads careers.json into memory (cached after first call)."""
    global _careers_cache
    if _careers_cache is None:
        with open(DATA_PATH, "r", encoding="utf-8") as f:
            _careers_cache = json.load(f)
    return _careers_cache


def get_career_by_id(career_id: int) -> dict | None:
    """Fetch a single career by its id."""
    careers = load_careers()
    for c in careers:
        if c["id"] == career_id:
            return c
    return None


def get_career_by_title(title: str) -> dict | None:
    """Fetch a single career by title (case-insensitive, exact match)."""
    careers = load_careers()
    for c in careers:
        if c["title"].lower() == title.lower():
            return c
    return None


def get_careers_by_category(category: str) -> list:
    """Fetch all careers belonging to a category."""
    careers = load_careers()
    return [c for c in careers if c["category"].lower() == category.lower()]


def get_all_categories() -> list:
    """Returns the unique list of categories in the dataset."""
    careers = load_careers()
    return sorted(set(c["category"] for c in careers))


if __name__ == "__main__":
    careers = load_careers()
    print(f"Loaded {len(careers)} careers")
    print(f"Categories: {get_all_categories()}")
    print(f"Example: {get_career_by_id(1)['title']}")
