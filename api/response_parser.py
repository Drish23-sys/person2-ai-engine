"""
response_parser.py
Safely parses JSON out of LLM text responses.
LLMs sometimes wrap JSON in markdown code fences (```json ... ```)
or add stray whitespace — this handles both cases.
"""

import json
import re


def parse_json_response(raw_response: str) -> dict | None:
    """
    Extracts and parses JSON from an LLM's raw text response.
    Returns None if parsing fails (caller should handle this case).
    """
    if not raw_response:
        return None

    cleaned = raw_response.strip()

    # Strip markdown code fences if present (```json ... ``` or ``` ... ```)
    if cleaned.startswith("```"):
        cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned)
        cleaned = re.sub(r"\s*```$", "", cleaned)

    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        # Last resort: try to find the first { ... last } block
        start = cleaned.find("{")
        end = cleaned.rfind("}")
        if start != -1 and end != -1 and end > start:
            try:
                return json.loads(cleaned[start:end + 1])
            except json.JSONDecodeError:
                return None
        return None


if __name__ == "__main__":
    # Test cases
    test1 = '{"a": 1, "b": 2}'
    test2 = '```json\n{"a": 1, "b": 2}\n```'
    test3 = 'Here is the result: {"a": 1, "b": 2} hope this helps!'
    test4 = 'not json at all'

    for t in [test1, test2, test3, test4]:
        print(f"Input: {t[:40]}... -> {parse_json_response(t)}")
