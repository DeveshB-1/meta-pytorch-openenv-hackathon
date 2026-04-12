"""
inference.py — OpenEnv baseline inference script for Tempo SQL Analytics Environment.

Runs all 3 tasks in-process using the OpenAI client with API_BASE_URL + MODEL_NAME.
Falls back to hardcoded template SQL if no API key is set.

Usage:
    python inference.py

Required env vars (optional — falls back to template if not set):
    API_BASE_URL   — LLM API endpoint (e.g. https://api.groq.com/openai/v1)
    MODEL_NAME     — Model identifier  (e.g. llama-3.3-70b-versatile)
    HF_TOKEN       — API key for the LLM provider

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

BENCHMARK_NAME = os.getenv("BENCHMARK_NAME", "tempo-sql-analytics-env")
SUCCESS_SCORE_THRESHOLD = float(os.getenv("SUCCESS_SCORE_THRESHOLD", "0.5"))

from src.environment.env import SQLQueryEnv
from src.tasks import ALL_TASKS, SCHEMA_DDL
from src.graders.task_easy_grader import grader as easy_grader
from src.graders.task_medium_grader import grader as medium_grader
from src.graders.task_hard_grader import grader as hard_grader
from src.graders.task_analytics_grader import grader as analytics_grader
from src.graders.task_realtime_grader import grader as realtime_grader
from src.graders.task_expert_grader import grader as expert_grader
from src.graders.task_iterative_grader import grader as iterative_grader
from src.graders.task_adversarial_grader import grader as adversarial_grader
from src.graders.task_pytorch_grader import grader as pytorch_grader
from src.baseline import BASELINE_QUERIES

GRADERS = {
    "task_easy":         easy_grader,
    "task_medium":       medium_grader,
    "task_hard":         hard_grader,
    "task_analytics":    analytics_grader,
    "task_realtime":     realtime_grader,
    "task_expert":       expert_grader,
    "task_iterative":    iterative_grader,
    "task_adversarial":  adversarial_grader,
    "task_pytorch":      pytorch_grader,
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
    api_key = HF_TOKEN or os.environ.get("OPENAI_API_KEY") or os.environ.get("API_KEY") or os.environ.get("GROQ_API_KEY")

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
        print(f"# LLM error: {e} — falling back to template", file=sys.stderr)
        return None


def main():
    use_llm = bool(HF_TOKEN or os.environ.get("OPENAI_API_KEY") or os.environ.get("API_KEY") or os.environ.get("GROQ_API_KEY"))

    env = SQLQueryEnv()
    all_scores = {}

    for task_id in ["task_easy", "task_medium", "task_hard", "task_analytics", "task_realtime", "task_expert", "task_iterative", "task_adversarial", "task_pytorch"]:
        # [START] line — exact required format
        print(f"[START] task={task_id} env={BENCHMARK_NAME} model={MODEL_NAME}")

        env.reset(task_id)
        task = ALL_TASKS[task_id]
        step_rewards = []
        n_questions = len(task.questions)

        for i, question in enumerate(task.questions):
            sql = None
            if use_llm:
                sql = ask_llm(question.text, question.columns)
            if sql is None:
                sql = BASELINE_QUERIES[question.id]

            action = {
                "action_type": "query",
                "payload": {"sql": sql, "question_id": question.id},
            }
            step_result = env.step(action)

            reward = step_result.reward
            error  = step_result.observation.get("error")
            done   = (i == n_questions - 1)

            action_str = json.dumps(action, separators=(",", ":"))
            error_str  = "null" if not error else str(error)
            done_str   = "true" if done else "false"

            # [STEP] line — exact required format
            print(f"[STEP] step={i+1} action={action_str} reward={reward:.2f} done={done_str} error={error_str}")
            step_rewards.append(reward)

        score   = GRADERS[task_id].grade(env.get_query_history())
        success = score >= SUCCESS_SCORE_THRESHOLD
        rewards_str = ",".join(f"{r:.2f}" for r in step_rewards)

        # [END] line — exact required format
        print(f"[END] success={'true' if success else 'false'} steps={n_questions} score={score:.3f} rewards={rewards_str}")
        all_scores[task_id] = score

    return all_scores


if __name__ == "__main__":
    main()
