"""
Baseline inference script.
Run this to produce reproducible scores before submission.
Usage: python scripts/run_baseline.py
"""
import httpx
import json

BASE_URL = "http://localhost:8000"
TASKS = ["task_easy", "task_medium", "task_hard"]


def run_episode(task_id: str) -> float:
    """Run a single episode for the given task and return score."""
    httpx.post(f"{BASE_URL}/reset")
    # TODO: Implement actual baseline agent logic here
    score = httpx.get(f"{BASE_URL}/grader", params={"task_id": task_id}).json()["score"]
    return score


def main():
    print("Running baseline inference...\n")
    scores = {}
    for task in TASKS:
        score = run_episode(task)
        scores[task] = score
        print(f"  {task}: {score:.4f}")

    print(f"\nBaseline scores: {json.dumps(scores, indent=2)}")
    return scores


if __name__ == "__main__":
    main()
