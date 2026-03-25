"""
Pre-submission validation script.
Run this before submitting to check all automated judge requirements.
Usage: python scripts/validate.py
"""
import httpx
import yaml
import sys

BASE_URL = "http://localhost:8000"
PASS = "✅"
FAIL = "❌"
results = []


def check(label: str, passed: bool, detail: str = ""):
    icon = PASS if passed else FAIL
    print(f"  {icon} {label}" + (f" — {detail}" if detail else ""))
    results.append(passed)


def main():
    print("\n🔍 Pre-submission validation\n")

    # 1. openenv.yaml exists and is valid
    try:
        with open("openenv.yaml") as f:
            config = yaml.safe_load(f)
        check("openenv.yaml valid", True)
        tasks = config.get("tasks", [])
        check("3+ tasks defined", len(tasks) >= 3, f"{len(tasks)} tasks found")
    except Exception as e:
        check("openenv.yaml valid", False, str(e))

    # 2. Server reachable
    try:
        r = httpx.get(f"{BASE_URL}/tasks", timeout=5)
        check("Server reachable", r.status_code == 200)
    except Exception as e:
        check("Server reachable", False, str(e))
        print("\n⚠️  Start the server first: uvicorn src.environment.server:app --host 0.0.0.0 --port 8000")
        sys.exit(1)

    # 3. /reset responds
    try:
        r = httpx.post(f"{BASE_URL}/reset", timeout=5)
        check("/reset returns 200", r.status_code == 200)
    except Exception as e:
        check("/reset returns 200", False, str(e))

    # 4. /tasks lists 3+ tasks
    try:
        r = httpx.get(f"{BASE_URL}/tasks", timeout=5)
        task_list = r.json().get("tasks", [])
        check("/tasks returns 3+ tasks", len(task_list) >= 3, f"{len(task_list)} returned")
    except Exception as e:
        check("/tasks returns 3+ tasks", False, str(e))

    # 5. /grader scores in 0.0–1.0 range
    try:
        r = httpx.get(f"{BASE_URL}/grader", params={"task_id": "task_easy"}, timeout=5)
        score = r.json().get("score", -1)
        check("Grader score in 0.0–1.0", 0.0 <= score <= 1.0, f"score={score}")
    except Exception as e:
        check("Grader score in 0.0–1.0", False, str(e))

    # 6. /baseline runs
    try:
        r = httpx.get(f"{BASE_URL}/baseline", timeout=30)
        check("/baseline returns 200", r.status_code == 200)
    except Exception as e:
        check("/baseline returns 200", False, str(e))

    passed = sum(results)
    total = len(results)
    print(f"\n{'='*40}")
    print(f"Result: {passed}/{total} checks passed")
    if passed == total:
        print("🎉 Ready to submit!")
    else:
        print("⚠️  Fix the failing checks before submitting.")
    print("="*40 + "\n")

    sys.exit(0 if passed == total else 1)


if __name__ == "__main__":
    main()
