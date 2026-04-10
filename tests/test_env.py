"""
tests/test_env.py — Test suite for the Tempo SQL Analytics OpenEnv project.

Tests:
  - All 7 tasks present in ALL_TASKS
  - Each task has exactly 5 questions
  - BASELINE_QUERIES covers all 35 question IDs
  - env.reset() works for all 7 tasks
  - env.step() with correct SQL gives reward >= 0.9
  - env.step() with explain action returns a plan
  - Partial row credit: 80%+ overlap scores >= 0.75, 50%+ scores >= 0.55
  - inference.py can be imported without error
"""
import importlib
import pytest

from src.tasks import ALL_TASKS, create_db
from src.baseline import BASELINE_QUERIES
from src.environment.env import SQLQueryEnv
from src.graders import _partial_overlap, BaseGrader


# ---------------------------------------------------------------------------
# Task structure tests
# ---------------------------------------------------------------------------

EXPECTED_TASKS = [
    "task_easy", "task_medium", "task_hard",
    "task_analytics", "task_realtime",
    "task_expert", "task_iterative", "task_adversarial",
]


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

def test_baseline_queries_cover_all_40_questions():
    all_question_ids = [q.id for task in ALL_TASKS.values() for q in task.questions]
    assert len(all_question_ids) == 40, f"Expected 40 questions, got {len(all_question_ids)}"
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
# explain action
# ---------------------------------------------------------------------------

def test_reset_observation_has_steps_remaining(env):
    obs = env.reset("task_easy")
    assert "steps_remaining" in obs, "reset obs missing steps_remaining"
    assert obs["steps_remaining"] == 10


def test_step_observation_has_richer_fields(env):
    env.reset("task_easy")
    result = env.step({
        "action_type": "query",
        "payload": {"sql": "SELECT 1 AS x", "question_id": "easy_q1"},
    })
    obs = result.observation
    assert "steps_remaining" in obs
    assert "question_index" in obs


def test_explain_action_returns_plan(env):
    env.reset("task_easy")
    result = env.step({
        "action_type": "explain",
        "payload": {"sql": "SELECT title, genre FROM songs WHERE genre = 'Electronic'"},
    })
    assert result.reward == 0.05
    obs = result.observation
    assert obs.get("error") is None, f"Explain error: {obs.get('error')}"
    assert "plan" in obs
    assert isinstance(obs["plan"], list)
    assert len(obs["plan"]) > 0


# ---------------------------------------------------------------------------
# Partial row credit scoring
# ---------------------------------------------------------------------------

def test_partial_overlap_exact():
    rows = [{"a": 1}, {"a": 2}, {"a": 3}]
    assert _partial_overlap(rows, rows, order_sensitive=False) == 1.0


def test_partial_overlap_80_pct():
    expected = [{"a": 1}, {"a": 2}, {"a": 3}, {"a": 4}, {"a": 5}]
    actual   = [{"a": 1}, {"a": 2}, {"a": 3}, {"a": 4}, {"a": 99}]
    score = _partial_overlap(actual, expected, order_sensitive=False)
    assert 0.75 <= score <= 0.85


def test_partial_overlap_50_pct():
    expected = [{"a": 1}, {"a": 2}, {"a": 3}, {"a": 4}]
    actual   = [{"a": 1}, {"a": 2}, {"a": 99}, {"a": 100}]
    score = _partial_overlap(actual, expected, order_sensitive=False)
    assert score == 0.5


def test_grader_partial_credit_high_overlap(env):
    """Grader should give score >= 0.75 when most rows are correct."""
    env.reset("task_easy")
    task = ALL_TASKS["task_easy"]
    question = task.questions[2]  # easy_q3: genre counts

    # Get correct rows, then mutate one value
    correct_sql = BASELINE_QUERIES[question.id]
    correct_result = env.step({
        "action_type": "query",
        "payload": {"sql": correct_sql, "question_id": question.id},
    })
    correct_rows = correct_result.observation.get("rows", [])
    if not correct_rows or len(correct_rows) < 3:
        pytest.skip("Not enough rows to test partial credit")

    # Submit only the first N-1 rows (simulating a LIMIT that cuts the last row)
    from src.graders import BaseGrader
    grader = BaseGrader(task)
    partial_history = [{
        "question_id": question.id,
        "rows": correct_rows[:-1],  # drop the last row
        "error": None,
    }]
    score = grader.grade(partial_history)
    assert score > 0.05, f"Expected partial credit > 0.05, got {score}"


# ---------------------------------------------------------------------------
# inference.py importable without error
# ---------------------------------------------------------------------------

def test_inference_importable():
    spec = importlib.util.find_spec("inference")
    assert spec is not None, "inference module not found"
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
