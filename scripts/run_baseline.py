"""
Baseline inference script — HTTP client that talks to the live server.
Run this to produce reproducible scores before submission.

Usage:
  uvicorn src.environment.server:app --host 0.0.0.0 --port 8000 &
  python scripts/run_baseline.py
"""
import json
import sys
import os

# Allow running from scripts/ directory
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import httpx

BASE_URL = "http://localhost:8000"
TASKS    = ["task_easy", "task_medium", "task_hard"]


def run_episode(client: httpx.Client, task_id: str) -> dict:
    """Run one full episode via HTTP and return score + per-question results."""

    # 1. Reset
    resp = client.post(f"{BASE_URL}/reset", json={"task_id": task_id})
    resp.raise_for_status()
    obs = resp.json()["observation"]
    questions = obs["questions"]

    results = []

    # 2. Submit one SQL query per question (uses server's baseline logic via /baseline
    #    would also work, but here we go step by step for visibility)
    from src.baseline import BASELINE_QUERIES
    import os
    from dotenv import load_dotenv
    load_dotenv()

    use_llm = bool(os.environ.get("GROQ_API_KEY"))

    for q in questions:
        if use_llm:
            from src.baseline import _ask_groq
            from src.tasks import ALL_TASKS
            task_q = next(tq for tq in ALL_TASKS[task_id].questions if tq.id == q["id"])
            sql = _ask_groq(task_q.text, task_q.columns) or BASELINE_QUERIES[q["id"]]
        else:
            sql = BASELINE_QUERIES[q["id"]]

        resp = client.post(f"{BASE_URL}/step", json={
            "action_type": "query",
            "payload":     {"sql": sql, "question_id": q["id"]},
        })
        resp.raise_for_status()
        step_result = resp.json()

        results.append({
            "question_id": q["id"],
            "reward":      step_result["reward"],
            "error":       step_result["observation"].get("error"),
        })

    # 3. Grade
    resp = client.get(f"{BASE_URL}/grader", params={"task_id": task_id})
    resp.raise_for_status()
    score = resp.json()["score"]

    return {"task_id": task_id, "score": score, "questions": results}


def main():
    print("Running baseline inference...\n")

    # Check server is up
    try:
        httpx.get(f"{BASE_URL}/health", timeout=3).raise_for_status()
    except Exception:
        print(f"ERROR: Server not reachable at {BASE_URL}")
        print("Start it with: uvicorn src.environment.server:app --host 0.0.0.0 --port 8000")
        sys.exit(1)

    all_scores = {}

    with httpx.Client(timeout=60) as client:
        for task_id in TASKS:
            print(f"--- {task_id} ---")
            episode = run_episode(client, task_id)

            for q in episode["questions"]:
                status = "CORRECT" if q["reward"] == 1.0 else ("ERROR" if q["error"] else "WRONG")
                print(f"  {q['question_id']}: {status}  (reward={q['reward']})")

            print(f"  Score: {episode['score']:.4f}\n")
            all_scores[task_id] = episode["score"]

    print("=" * 35)
    print(f"Average: {sum(all_scores.values()) / len(all_scores):.4f}")
    print("=" * 35)
    print(json.dumps(all_scores, indent=2))
    return all_scores


if __name__ == "__main__":
    main()
