"""
career_recommender.py
Module 2 of the AI Engine — the core recommendation logic.
Takes student profile + interest scores, sends a prompt to the LLM
with the full careers dataset, and returns the top 3 ranked careers.
"""

import json
from llm_client import safe_llm_call
from data_loader import load_careers
from response_parser import parse_json_response


RECOMMENDER_SYSTEM_PROMPT = """You are an expert career counselor for students
in India. You analyze a student's profile, quiz answers and interest scores,
then recommend the most suitable career paths from a provided database.

Rules:
- Only recommend careers that exist in the provided database — never invent one.
- Respond with valid JSON only. No explanation outside the JSON.
- Match percentages should be realistic and vary meaningfully between
  recommendations (avoid giving every option 90%+).
- skill_gaps must only include skills from that career's required_skills list
  that the student likely does NOT already have, based on their profile.
"""


def build_recommender_prompt(student: dict, quiz_answers: dict, interest_scores: dict) -> str:
    """
    Builds the prompt sent to the LLM for the final career recommendation step.
    Pulls the full dataset in from Person 4's careers.json via data_loader.
    """
    careers = load_careers()

    # Trim the dataset payload to just what the LLM needs to decide & cite —
    # keeps the prompt smaller and faster.
    trimmed_careers = [
        {
            "id": c["id"],
            "title": c["title"],
            "category": c["category"],
            "description": c["description"],
            "required_skills": c["required_skills"],
            "difficulty_level": c["difficulty_level"],
            "avg_salary_range": c["avg_salary_range"],
            "demand_level": c["demand_level"],
            "courses": c["courses"]
        }
        for c in careers
    ]

    return f"""
Student Profile:
- Name: {student.get('name', 'Student')}
- Education level: {student.get('education', 'Not specified')}
- Age: {student.get('age', 'Not specified')}

Quiz Answers:
- Favorite subjects: {quiz_answers.get('subjects', [])}
- Interests: {quiz_answers.get('interests', [])}
- Strengths: {quiz_answers.get('strengths', [])}
- Preferred work style: {quiz_answers.get('work_style', 'Not specified')}
- Career goal: {quiz_answers.get('goal', 'Not specified')}

Interest Scores (0-100 per category):
{json.dumps(interest_scores, indent=2)}

Available Careers Database:
{json.dumps(trimmed_careers, indent=2)}

Based on all the above, recommend the top 3 most suitable careers
for this student from the database above ONLY.

Respond ONLY in this JSON format:
{{
  "recommendations": [
    {{
      "rank": 1,
      "career_id": 0,
      "career_title": "",
      "match_percentage": 0,
      "reason": "ONE short sentence (max 20 words) explaining the fit for this student",
      "required_skills": [],
      "skill_gaps": [],
      "suggested_courses": [
        {{"name": "", "provider": "", "link": ""}}
      ]
    }}
  ],
  "summary": "One line overall summary for the student"
}}
"""


def recommend_careers(student: dict, quiz_answers: dict, interest_scores: dict) -> dict:
    """
    Main function: takes student profile + quiz answers + interest scores,
    returns the top 3 career recommendations.
    Includes retry logic for when Gemini doesn't return clean/complete JSON.
    """
    prompt = build_recommender_prompt(student, quiz_answers, interest_scores)

    for attempt in range(3):  # retry up to 3 times, same pattern as interest_analyzer.py
        result = safe_llm_call(prompt, system_prompt=RECOMMENDER_SYSTEM_PROMPT, max_tokens=8192)

        if not result["success"]:
            return {"success": False, "recommendations": [], "summary": None, "error": result["error"]}

        parsed = parse_json_response(result["raw_response"])

        if parsed is not None:
            recommendations = parsed.get("recommendations", [])
            valid_ids = {c["id"] for c in load_careers()}
            recommendations = [r for r in recommendations if r.get("career_id") in valid_ids]

            return {
                "success": True,
                "recommendations": recommendations,
                "summary": parsed.get("summary", ""),
                "error": None
            }

        print(f"---- RECOMMENDER parse failed (attempt {attempt + 1}) ----")
        print(result["raw_response"])
        print("------------------------------------------------------------")

    return {"success": False, "recommendations": [], "summary": None,
             "error": "Could not parse LLM response as JSON after 3 attempts"}

if __name__ == "__main__":
    sample_student = {"name": "Drish", "education": "B.Tech, IV Semester", "age": 20}
    sample_answers = {
        "subjects": ["Mathematics", "Computer Science"],
        "interests": ["coding", "AI", "building apps"],
        "strengths": ["logical thinking", "problem solving"],
        "work_style": "Remote, independent work",
        "goal": "High-growth tech career"
    }
    sample_scores = {
        "Engineering & Technology": 92,
        "Health, Emerging & Future Careers": 20,
        "Social Impact & Human Services": 15,
        "Finance & Commerce": 30,
        "Marketing & Sales": 25,
        "Science & Research": 60
    }
    print(json.dumps(recommend_careers(sample_student, sample_answers, sample_scores), indent=2))
