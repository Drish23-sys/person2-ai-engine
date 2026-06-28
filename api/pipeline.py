"""
pipeline.py
The single entry point Person 3 (Backend) will call from the API route.
Runs the full AI flow: quiz answers -> interest analysis -> recommendations.
"""

from interest_analyzer import analyze_interests
from career_recommender import recommend_careers


def run_career_pipeline(student: dict, quiz_answers: dict) -> dict:
    """
    Full pipeline: student profile + quiz answers -> final recommendations.

    This is the function Person 3 calls from the backend, e.g.:
        POST /quiz/submit -> run_career_pipeline(student, answers) -> save + return result

    Returns a single dict with everything the frontend needs.
    """
    # Step 1: Interest Analyzer
    interest_result = analyze_interests(quiz_answers)
    if not interest_result["success"]:
        return {
            "success": False,
            "stage_failed": "interest_analysis",
            "error": interest_result["error"]
        }

    # Step 2: Career Recommender (uses output of Step 1)
    recommendation_result = recommend_careers(
        student,
        quiz_answers,
        interest_result["interest_scores"]
    )
    if not recommendation_result["success"]:
        return {
            "success": False,
            "stage_failed": "recommendation",
            "error": recommendation_result["error"]
        }

    # Combine both results into the final payload
    return {
        "success": True,
        "interest_scores": interest_result["interest_scores"],
        "interest_summary": interest_result["top_interest_summary"],
        "recommendations": recommendation_result["recommendations"],
        "overall_summary": recommendation_result["summary"]
    }


if __name__ == "__main__":
    import json

    sample_student = {"name": "Drish", "education": "B.Tech, IV Semester", "age": 20}
    sample_answers = {
        "subjects": ["Biology", "Chemistry"],
        "interests": ["helping people", "healthcare", "research"],
        "strengths": ["empathy", "attention to detail"],
        "work_style": "In-person, patient-facing",
        "goal": "Make a direct impact on people's lives"
    }

    result = run_career_pipeline(sample_student, sample_answers)
    print(json.dumps(result, indent=2))
