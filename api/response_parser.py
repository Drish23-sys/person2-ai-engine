"""
response_parser.py
Safely parses JSON out of LLM text responses.
LLMs sometimes wrap JSON in markdown code fences (```json ... ```)
or add stray whitespace — this handles both cases.
"""

import json
import re


def parse_json_response(raw_response: str) -> dict | None:
    if not raw_response:
        return None

    cleaned = raw_response.strip()

    # Remove ALL variations of markdown code fences
    # Handles ```json, ```JSON, ```, and anything in between
    cleaned = re.sub(r'^```[a-zA-Z]*\s*', '', cleaned)
    cleaned = re.sub(r'\s*```$', '', cleaned)
    cleaned = cleaned.strip()

    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        # Last resort: find first { to last }
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
