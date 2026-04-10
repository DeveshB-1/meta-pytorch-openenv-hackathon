"""
tests/test_env.py — Test suite for the Tempo SQL Analytics OpenEnv project.

Tests:
  - All 5 tasks present in ALL_TASKS
  - Each task has exactly 5 questions
  - BASELINE_QUERIES covers all 25 question IDs
  - env.reset() works for all 5 tasks
  - env.step() with correct SQL gives reward >= 0.9
  - inference.py can be imported without error
"""
import importlib
import pytest

from src.tasks import ALL_TASKS, create_db
from src.baseline import BASELINE_QUERIES
from src.environment.env import SQLQueryEnv


# ---------------------------------------------------------------------------
# Task structure tests
# ---------------------------------------------------------------------------

EXPECTED_TASKS = ["task_easy", "task_medium", "task_hard", "task_analytics", "task_realtime"]


def test_all_tasks_present():
    for task_id in EXPECTED_TASKS:
        assert task_id in ALL_TASKS, f"Missing task: {task_id}"


def test_each_task_has_five_questions():
    for task_id in EXPECTED_TASKS:
        task = ALL_TASKS[task_id]
        assert len(task.questions) == 5, (
            f"{task_id} has {len(task.questions)} questions, expected 5"
        )


def test_all_question_ids_unique():
    all_ids = [q.id for task in ALL_TASKS.values() for q in task.questions]
    assert len(all_ids) == len(set(all_ids)), "Duplicate question IDs found"


# ---------------------------------------------------------------------------
# Baseline queries coverage
# ---------------------------------------------------------------------------

def test_baseline_queries_cover_all_25_questions():
    all_question_ids = [q.id for task in ALL_TASKS.values() for q in task.questions]
    assert len(all_question_ids) == 25, f"Expected 25 questions, got {len(all_question_ids)}"
    for qid in all_question_ids:
        assert qid in BASELINE_QUERIES, f"BASELINE_QUERIES missing key: {qid}"


# ---------------------------------------------------------------------------
# Environment reset tests
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module")
def env():
    return SQLQueryEnv()


@pytest.mark.parametrize("task_id", EXPECTED_TASKS)
def test_env_reset(env, task_id):
    obs = env.reset(task_id)
    assert obs is not None
    assert "schema" in obs
    assert "questions" in obs
    assert len(obs["questions"]) == 5


# ---------------------------------------------------------------------------
# env.step() with correct SQL gives reward >= 0.9
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("task_id", EXPECTED_TASKS)
def test_env_step_correct_sql_reward(env, task_id):
    env.reset(task_id)
    task = ALL_TASKS[task_id]
    for question in task.questions:
        sql = BASELINE_QUERIES[question.id]
        result = env.step({
            "action_type": "query",
            "payload": {
                "sql": sql,
                "question_id": question.id,
            },
        })
        assert result.reward >= 0.9, (
            f"{question.id}: expected reward >= 0.9, got {result.reward}. "
            f"Error: {result.observation.get('error')}"
        )


# ---------------------------------------------------------------------------
# inference.py importable without error
# ---------------------------------------------------------------------------

def test_inference_importable():
    spec = importlib.util.find_spec("inference")
    assert spec is not None, "inference module not found"
    # Import it — this should not raise
    mod = importlib.import_module("inference")
    assert hasattr(mod, "main"), "inference.py should have a main() function"


# ---------------------------------------------------------------------------
# DB sanity check
# ---------------------------------------------------------------------------

def test_create_db_row_counts():
    conn = create_db()
    expected = {
        "artists": 30,
        "songs": 110,
        "users": 75,
        "streams": 650,
        "playlists": 50,
        "playlist_songs": 132,
    }
    for table, min_count in expected.items():
        count = conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
        assert count >= min_count, f"{table}: expected >= {min_count} rows, got {count}"
    conn.close()
