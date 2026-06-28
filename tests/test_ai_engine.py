"""
test_ai_engine.py
Run with: pytest test_ai_engine.py -v

These tests don't all require a live API key — the parser and prompt
builder tests run offline. Mark API-dependent tests so you can skip
them when you don't want to burn API credits.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "api"))

import pytest
from response_parser import parse_json_response
from data_loader import load_careers, get_career_by_id, get_all_categories
from interest_analyzer import build_analyzer_prompt
from career_recommender import build_recommender_prompt


# ---------- Offline tests (no API key needed) ----------

def test_parse_clean_json():
    result = parse_json_response('{"a": 1}')
    assert result == {"a": 1}


def test_parse_markdown_wrapped_json():
    result = parse_json_response('```json\n{"a": 1}\n```')
    assert result == {"a": 1}


def test_parse_json_with_surrounding_text():
    result = parse_json_response('Here you go: {"a": 1} thanks!')
    assert result == {"a": 1}


def test_parse_invalid_json_returns_none():
    result = parse_json_response('this is not json')
    assert result is None


def test_dataset_loads():
    careers = load_careers()
    assert len(careers) == 30


def test_dataset_has_unique_ids():
    careers = load_careers()
    ids = [c["id"] for c in careers]
    assert len(ids) == len(set(ids))


def test_get_career_by_id():
    career = get_career_by_id(1)
    assert career is not None
    assert career["title"] == "Software Engineer"


def test_get_career_by_id_invalid():
    career = get_career_by_id(9999)
    assert career is None


def test_categories_present():
    categories = get_all_categories()
    assert "Engineering & Technology" in categories
    assert len(categories) == 6


def test_build_analyzer_prompt_contains_student_data():
    answers = {"subjects": ["Math", "CS"], "interests": ["coding"],
               "strengths": ["logic"], "work_style": "remote", "goal": "tech job"}
    prompt = build_analyzer_prompt(answers)
    assert "Math" in prompt
    assert "coding" in prompt


def test_build_recommender_prompt_contains_dataset():
    student = {"name": "Test Student", "education": "B.Tech", "age": 20}
    answers = {"subjects": ["Math"], "interests": ["coding"], "strengths": ["logic"],
               "work_style": "remote", "goal": "tech job"}
    scores = {"Engineering & Technology": 90}
    prompt = build_recommender_prompt(student, answers, scores)
    assert "Test Student" in prompt
    assert "Software Engineer" in prompt  # confirms dataset got pulled in


# ---------- Live API tests (require ANTHROPIC_API_KEY, cost real calls) ----------

@pytest.mark.skip(reason="Requires live API key — unskip to test manually")
def test_full_pipeline_live():
    from pipeline import run_career_pipeline
    student = {"name": "Test Student", "education": "B.Tech", "age": 20}
    answers = {"subjects": ["Math", "CS"], "interests": ["coding", "AI"],
               "strengths": ["logic"], "work_style": "remote", "goal": "tech career"}
    result = run_career_pipeline(student, answers)
    assert result["success"] is True
    assert len(result["recommendations"]) > 0
