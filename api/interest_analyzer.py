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


ANALYZER_SYSTEM_PROMPT = """You are a career interest analysis engine.
Output ONLY a single valid JSON object. 
No markdown, no code fences, no explanation, no extra text.
Just the raw JSON object starting with { and ending with }.

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
    Includes retry logic for when Gemini doesn't return clean JSON.
    """
    prompt = build_analyzer_prompt(quiz_answers)
    
    for attempt in range(3):  # retry up to 3 times
        result = safe_llm_call(prompt, system_prompt=ANALYZER_SYSTEM_PROMPT, max_tokens=1500)

        if not result["success"]:
            return {"success": False, "interest_scores": None, 
                    "top_interest_summary": None, "error": result["error"]}

        parsed = parse_json_response(result["raw_response"])
        
        if parsed is not None:
            return {
                "success": True,
                "interest_scores": parsed.get("interest_scores", {}),
                "top_interest_summary": parsed.get("top_interest_summary", ""),
                "error": None
            }
        
        # If parsing failed, print raw response for debugging
        print(f"---- INTEREST ANALYZER parse failed (attempt {attempt + 1}) ----")
        print(result["raw_response"])
        print("----------------------------------------------------------------")

    return {
        "success": False,
        "interest_scores": None,
        "top_interest_summary": None,
        "error": "Could not parse LLM response as JSON after 3 attempts"
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
