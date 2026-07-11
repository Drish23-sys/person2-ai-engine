

import os
from google import genai
from dotenv import load_dotenv

load_dotenv()

# Gemini 2.5 Flash has the most generous free-tier limits and strong quality.
MODEL_NAME = "gemini-2.5-flash"

_client = None


def _get_client():
    """
    Lazily creates the Gemini client on first use, rather than at import time.
    This means importing llm_client.py never crashes even if no API key is
    set yet (e.g. during testing or before .env is configured) — the error
    only surfaces when you actually try to make a call.
    """
    global _client
    if _client is None:
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError(
                "GEMINI_API_KEY not found. Add it to your .env file. "
                "Get a free key at https://aistudio.google.com"
            )
        _client = genai.Client(api_key=api_key)
    return _client


def call_llm(prompt: str, system_prompt: str = "", max_tokens: int = 1500) -> str:
    """
    Sends a prompt to Gemini and returns the raw text response.

    Args:
        prompt: the user-facing prompt (student data + question)
        system_prompt: instructions that set the AI's role/behavior
        max_tokens: response length limit

    Returns:
        Raw text response from Gemini (may include markdown formatting)
    """
    response = _get_client().models.generate_content(
        model=MODEL_NAME,
        contents=prompt,
        config={
            "system_instruction": system_prompt,
            "max_output_tokens": max_tokens,
            "temperature": 0.7,
        }
    )
    return response.text


def safe_llm_call(prompt: str, system_prompt: str = "", max_tokens: int = 1500) -> dict:
    """
    Wraps call_llm() with error handling so a failed API call
    never crashes your backend — it just returns an error dict instead.
    """
    try:
        response = call_llm(prompt, system_prompt, max_tokens=max_tokens)
        return {"success": True, "raw_response": response}
    except ValueError as e:
        # Raised by _get_client() when GEMINI_API_KEY is missing
        return {"success": False, "error": str(e)}
    except Exception as e:
        error_msg = str(e)
        if "RESOURCE_EXHAUSTED" in error_msg or "429" in error_msg:
            return {"success": False, "error": "Rate limit reached on the free tier. Wait a minute and try again."}
        elif "API_KEY_INVALID" in error_msg or "401" in error_msg or "403" in error_msg:
            return {"success": False, "error": "Invalid API key. Check your .env file (GEMINI_API_KEY)."}
        elif "Connection" in error_msg:
            return {"success": False, "error": "Could not connect to the AI service. Check your internet connection."}
        else:
            return {"success": False, "error": f"Unexpected error: {error_msg}"}


if __name__ == "__main__":
    # Quick manual test — run: python llm_client.py
    result = safe_llm_call("Say hello in one sentence.")
    print(result)
