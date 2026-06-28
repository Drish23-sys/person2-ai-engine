"""
interest_analyzer.py
Module 1 of the AI Engine.
Takes raw quiz answers and converts them into structured interest scores
across the dataset's categories using the LLM.
"""

import json
from llm_client import safe_llm_call
from data_loader import get_all_categories
from response_parser import parse_json_response


ANALYZER_SYSTEM_PROMPT = """You are a career interest analysis engine for an
Indian student career-guidance platform. You read a student's quiz answers
and output ONLY valid JSON describing their interest profile.

Rules:
- Respond with valid JSON only. No explanation, no markdown formatting, no preamble.
- Scores must be integers from 0 to 100.
- Every category listed must appear in your output, even if the score is low.
"""


def build_analyzer_prompt(quiz_answers: dict) -> str:
    """
    Builds the prompt sent to the LLM to score student interests
    against each category present in the dataset.
    """
    categories = get_all_categories()

    return f"""
Student quiz answers:
- Favorite subjects: {quiz_answers.get('subjects', [])}
- Interests: {quiz_answers.get('interests', [])}
- Strengths: {quiz_answers.get('strengths', [])}
- Preferred work style: {quiz_answers.get('work_style', 'Not specified')}
- Career goal: {quiz_answers.get('goal', 'Not specified')}

Categories to score against:
{json.dumps(categories, indent=2)}

Score the student's interest in EACH category above from 0-100, based on
how well their subjects/interests/strengths align with that category.

Respond ONLY in this JSON format:
{{
  "interest_scores": {{
    "Engineering & Technology": 0,
    "Health, Emerging & Future Careers": 0,
    "Social Impact & Human Services": 0,
    "Finance & Commerce": 0,
    "Marketing & Sales": 0,
    "Science & Research": 0
  }},
  "top_interest_summary": "One sentence describing the student's dominant interest area"
}}
"""


def analyze_interests(quiz_answers: dict) -> dict:
    """
    Main function: takes quiz answers, returns interest scores.

    Returns:
        {
          "success": bool,
          "interest_scores": {...} or None,
          "top_interest_summary": str or None,
          "error": str or None
        }
    """
    prompt = build_analyzer_prompt(quiz_answers)
    result = safe_llm_call(prompt, system_prompt=ANALYZER_SYSTEM_PROMPT)

    if not result["success"]:
        return {"success": False, "interest_scores": None, "top_interest_summary": None, "error": result["error"]}

    parsed = parse_json_response(result["raw_response"])
    if parsed is None:
        return {"success": False, "interest_scores": None, "top_interest_summary": None,
                 "error": "Could not parse LLM response as JSON"}

    return {
        "success": True,
        "interest_scores": parsed.get("interest_scores", {}),
        "top_interest_summary": parsed.get("top_interest_summary", ""),
        "error": None
    }


if __name__ == "__main__":
    # Quick manual test
    sample_answers = {
        "subjects": ["Mathematics", "Computer Science"],
        "interests": ["coding", "building apps", "puzzles"],
        "strengths": ["logical thinking", "problem solving"],
        "work_style": "Remote, independent work",
        "goal": "High-growth tech career"
    }
    print(json.dumps(analyze_interests(sample_answers), indent=2))
