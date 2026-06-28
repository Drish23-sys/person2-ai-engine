# Person 2 — AI Engine

## Setup

This project uses **Google Gemini API** (free tier, no credit card required).

```bash
pip install -r requirements.txt --break-system-packages
cp .env.example .env
# then paste your real Gemini API key into .env
```

### Get your free API key
1. Go to https://aistudio.google.com
2. Sign in with your Google account
3. Click "Get API key" → "Create API key in new project"
4. Copy the key into `.env` as `GEMINI_API_KEY=...`

No card needed. The free tier has daily/per-minute rate limits, but they're
more than enough for development and a class demo.

## Folder structure

```
person2_ai_engine/
├── api/
│   ├── llm_client.py          <- calls the Claude API (lowest level)
│   ├── data_loader.py         <- loads Person 4's careers.json
│   ├── response_parser.py     <- safely parses JSON out of LLM replies
│   ├── interest_analyzer.py   <- Module 1: quiz answers -> interest scores
│   ├── career_recommender.py  <- Module 2: scores -> top 3 careers
│   └── pipeline.py            <- combines both modules into ONE function
├── data/
│   └── careers.json           <- dataset from Person 4
├── tests/
│   └── test_ai_engine.py
├── .env                       <- your API key (never commit this)
├── .env.example
└── requirements.txt
```

## How to run

Test each piece individually first:
```bash
cd api
python llm_client.py        # confirms API key works
python data_loader.py       # confirms dataset loads correctly
python response_parser.py   # offline parser tests
python interest_analyzer.py # live test — calls the API
python career_recommender.py # live test — calls the API
python pipeline.py          # full end-to-end live test
```

Run automated tests:
```bash
cd tests
pytest test_ai_engine.py -v
```

## What Person 3 (Backend) needs from you

A single function: `run_career_pipeline(student, quiz_answers)` from `pipeline.py`.
They call it after quiz submission and get back:

```python
{
  "success": True,
  "interest_scores": {...},
  "interest_summary": "...",
  "recommendations": [...top 3 careers...],
  "overall_summary": "..."
}
```

They don't need to know anything about prompts, the LLM, or the dataset —
this one function is your entire API surface to the rest of the team.
