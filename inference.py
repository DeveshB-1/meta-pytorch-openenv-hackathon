"""
inference.py — OpenEnv baseline inference script for Tempo SQL Analytics Environment.

Runs all 3 tasks in-process using the OpenAI client with API_BASE_URL + MODEL_NAME.
Falls back to hardcoded template SQL if no API key is set.

Usage:
    python inference.py

Required env vars (optional — falls back to template if not set):
    API_BASE_URL   — LLM API endpoint (e.g. https://api.groq.com/openai/v1)
    MODEL_NAME     — Model identifier  (e.g. llama-3.3-70b-versatile)
    OPENAI_API_KEY — API key for the LLM provider

Runtime: < 2 minutes (template mode) or < 5 minutes (LLM mode)
Hardware: runs comfortably on 2 vCPU / 8 GB RAM
"""
import json
import os
import sys

from dotenv import load_dotenv
load_dotenv()

from src.environment.env import SQLQueryEnv
from src.tasks import ALL_TASKS, SCHEMA_DDL
from src.graders.task_easy_grader import grader as easy_grader
from src.graders.task_medium_grader import grader as medium_grader
from src.graders.task_hard_grader import grader as hard_grader
from src.baseline import BASELINE_QUERIES

GRADERS = {
    "task_easy":   easy_grader,
    "task_medium": medium_grader,
    "task_hard":   hard_grader,
}

SYSTEM_PROMPT = """You are a SQLite SQL expert. Given a database schema and a question, write a single SQL query that answers the question exactly.

Rules:
- Return ONLY the SQL query, no explanation, no markdown, no code fences
- Use exact column aliases as specified in the question
- The database is SQLite (supports window functions)
- Do not add a semicolon at the end
"""


def ask_llm(question_text: str, columns: list) -> str | None:
    """Ask LLM to write SQL using OpenAI client + API_BASE_URL/MODEL_NAME env vars."""
    api_key  = os.environ.get("OPENAI_API_KEY") or os.environ.get("API_KEY")
    api_base = os.environ.get("API_BASE_URL", "https://api.openai.com/v1")
    model    = os.environ.get("MODEL_NAME", "gpt-4o-mini")

    if not api_key:
        return None

    try:
        from openai import OpenAI
        client = OpenAI(api_key=api_key, base_url=api_base)

        user_msg = (
            f"Schema:\n{SCHEMA_DDL}\n\n"
            f"Question: {question_text}\n"
            f"Expected output columns: {', '.join(columns)}\n\n"
            f"Write the SQL query:"
        )

        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user",   "content": user_msg},
            ],
            temperature=0,
            max_tokens=512,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"[inference] LLM error: {e} — falling back to template")
        return None


def run_task(env: SQLQueryEnv, task_id: str, use_llm: bool) -> dict:
    """Run one full episode and return score + per-question breakdown."""
    env.reset(task_id)
    task = ALL_TASKS[task_id]

    results = []
    for question in task.questions:
        sql = None

        if use_llm:
            sql = ask_llm(question.text, question.columns)

        if sql is None:
            sql = BASELINE_QUERIES[question.id]

        step_result = env.step({
            "action_type": "query",
            "payload": {
                "sql":         sql,
                "question_id": question.id,
            },
        })

        reward = step_result.reward
        error  = step_result.observation.get("error")
        status = "CORRECT" if reward == 1.0 else ("ERROR" if error else "WRONG")

        results.append({
            "question_id": question.id,
            "status":      status,
            "reward":      reward,
            "error":       error,
        })

    score = GRADERS[task_id].grade(env.get_query_history())
    return {"task_id": task_id, "score": score, "questions": results}


def main():
    use_llm = bool(
        os.environ.get("OPENAI_API_KEY") or os.environ.get("API_KEY")
    )
    mode = "llm" if use_llm else "template"

    print(f"Tempo SQL Analytics — OpenEnv Baseline Inference")
    print(f"Mode: {mode}")
    if use_llm:
        print(f"  API_BASE_URL = {os.environ.get('API_BASE_URL', 'https://api.openai.com/v1')}")
        print(f"  MODEL_NAME   = {os.environ.get('MODEL_NAME', 'gpt-4o-mini')}")
    print()

    env = SQLQueryEnv()
    all_scores = {}

    for task_id in ["task_easy", "task_medium", "task_hard"]:
        print(f"--- {task_id} ---")
        episode = run_task(env, task_id, use_llm)

        for q in episode["questions"]:
            print(f"  {q['question_id']}: {q['status']}  (reward={q['reward']})")

        print(f"  Score: {episode['score']:.4f}\n")
        all_scores[task_id] = episode["score"]

    avg = sum(all_scores.values()) / len(all_scores)
    print("=" * 40)
    print(f"Average score: {avg:.4f}")
    print("=" * 40)
    print(json.dumps({"mode": mode, "scores": all_scores}, indent=2))

    return all_scores


if __name__ == "__main__":
    main()
