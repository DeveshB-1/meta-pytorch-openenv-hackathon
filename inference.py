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

API_BASE_URL = os.getenv("API_BASE_URL", "https://api.groq.com/openai/v1")
MODEL_NAME = os.getenv("MODEL_NAME", "llama-3.3-70b-versatile")
HF_TOKEN = os.getenv("HF_TOKEN")
LOCAL_IMAGE_NAME = os.getenv("LOCAL_IMAGE_NAME")

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
    api_key = os.environ.get("OPENAI_API_KEY") or os.environ.get("API_KEY") or os.environ.get("GROQ_API_KEY")

    if not api_key:
        return None

    try:
        from openai import OpenAI
        client = OpenAI(api_key=api_key, base_url=API_BASE_URL)

        user_msg = (
            f"Schema:\n{SCHEMA_DDL}\n\n"
            f"Question: {question_text}\n"
            f"Expected output columns: {', '.join(columns)}\n\n"
            f"Write the SQL query:"
        )

        response = client.chat.completions.create(
            model=MODEL_NAME,
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
        os.environ.get("OPENAI_API_KEY") or os.environ.get("API_KEY") or os.environ.get("GROQ_API_KEY")
    )
    mode = "llm" if use_llm else "template"

    print(f"[START] mode={mode} api_base_url={API_BASE_URL} model_name={MODEL_NAME}")

    env = SQLQueryEnv()
    all_scores = {}

    for task_id in ["task_easy", "task_medium", "task_hard"]:
        print(f"[START] task_id={task_id}")
        episode = run_task(env, task_id, use_llm)

        for q in episode["questions"]:
            r = max(0.0001, min(0.9999, q['reward']))
            print(f"[STEP] task_id={task_id} question_id={q['question_id']} status={q['status']} reward={r}")

        print(f"[END] task_id={task_id} score={episode['score']:.4f}")
        all_scores[task_id] = episode["score"]

    avg = sum(all_scores.values()) / len(all_scores)
    print(f"[END] mode={mode} avg_score={avg:.4f} scores={json.dumps(all_scores)}")

    return all_scores


if __name__ == "__main__":
    main()
