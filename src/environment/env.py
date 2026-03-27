"""
Base OpenEnv environment implementation.
Implements the standard step() / reset() / state() API.
"""
import sqlite3
from abc import ABC, abstractmethod
from typing import Any

from pydantic import BaseModel

from src.tasks import ALL_TASKS, TaskDef, create_db, SCHEMA_DDL
from src.graders import rows_match, SCORE_MAP

MAX_STEPS = 10


class StepResult(BaseModel):
    observation: dict[str, Any]
    reward: float
    done: bool
    info: dict[str, Any] = {}


class HackathonEnv(ABC):
    """Abstract base class for all OpenEnv environments."""

    def __init__(self):
        self._state: dict[str, Any] = {}

    @abstractmethod
    def reset(self) -> dict[str, Any]:
        """Reset environment to initial state. Returns initial observation."""
        ...

    @abstractmethod
    def step(self, action: dict[str, Any]) -> StepResult:
        """Execute action. Returns observation, reward, done flag, info."""
        ...

    def state(self) -> dict[str, Any]:
        """Return current environment state."""
        return self._state


class SQLQueryEnv(HackathonEnv):
    """
    OpenEnv environment where an agent writes SQL queries to answer
    natural language questions about an in-memory SQLite database.
    """

    def __init__(self):
        super().__init__()
        self.conn: sqlite3.Connection = create_db()  # always live
        self.current_task: TaskDef | None = None
        self.step_count: int = 0
        self.query_history: list[dict] = []

    # ------------------------------------------------------------------
    # reset
    # ------------------------------------------------------------------

    def reset(self, task_id: str = "task_easy") -> dict[str, Any]:
        """Start a fresh episode. Returns initial observation with schema + questions."""
        if task_id not in ALL_TASKS:
            raise ValueError(f"Unknown task_id '{task_id}'. Choose from: {list(ALL_TASKS)}")

        if self.conn:
            self.conn.close()

        self.conn = create_db()
        self.current_task = ALL_TASKS[task_id]
        self.step_count = 0
        self.query_history = []

        return {
            "task_id":   self.current_task.id,
            "task_name": self.current_task.name,
            "schema":    SCHEMA_DDL,
            "questions": [
                {"id": q.id, "text": q.text, "columns": q.columns}
                for q in self.current_task.questions
            ],
            "step":      self.step_count,
            "max_steps": MAX_STEPS,
        }

    # ------------------------------------------------------------------
    # step
    # ------------------------------------------------------------------

    def step(self, action: dict[str, Any]) -> StepResult:
        """
        Process one agent action.

        Action types:
          query → {"action_type": "query", "payload": {"sql": "...", "question_id": "easy_q1"}}
          hint  → {"action_type": "hint",  "payload": {"type": "schema"}}
                  {"action_type": "hint",  "payload": {"type": "sample_rows", "table": "employees"}}
        """
        if self.current_task is None:
            return StepResult(
                observation={"error": "Environment not reset. Call /reset first."},
                reward=0.0, done=True, info={}
            )

        self.step_count += 1
        done = self.step_count >= MAX_STEPS
        action_type = action.get("action_type", "query")
        payload = action.get("payload", {})

        if action_type == "hint":
            obs = self._handle_hint(payload)
            return StepResult(observation=obs, reward=0.0, done=done, info={"action_type": "hint"})

        # Default: query
        sql = payload.get("sql", "")
        question_id = payload.get("question_id", "")
        rows, error = self._execute_sql(sql)

        # Intermediate reward
        reward = 0.0
        if error:
            reward = -0.01
        elif rows:
            reward = 0.05  # non-empty result — making progress

        # Check if this is a correct answer
        question = next((q for q in self.current_task.questions if q.id == question_id), None)
        if question and not error:
            matched, reason = rows_match(rows, question.expected_rows, question.order_sensitive)
            if matched:
                reward = 1.0

        # Record in history (grader reads this later)
        self.query_history.append({
            "question_id": question_id,
            "sql":         sql,
            "rows":        rows,
            "error":       error,
        })

        obs = {
            "task_id":     self.current_task.id,
            "question_id": question_id,
            "rows":        rows,
            "error":       error,
            "step":        self.step_count,
            "max_steps":   MAX_STEPS,
        }
        return StepResult(observation=obs, reward=reward, done=done, info={})

    # ------------------------------------------------------------------
    # state
    # ------------------------------------------------------------------

    def state(self) -> dict[str, Any]:
        """Return a snapshot of the current environment state."""
        return {
            "task_id":       self.current_task.id if self.current_task else None,
            "step":          self.step_count,
            "max_steps":     MAX_STEPS,
            "history_count": len(self.query_history),
            "questions": [
                {"id": q.id, "text": q.text}
                for q in self.current_task.questions
            ] if self.current_task else [],
        }

    # ------------------------------------------------------------------
    # helpers
    # ------------------------------------------------------------------

    def _execute_sql(self, sql: str) -> tuple[list[dict] | None, str | None]:
        """Run SQL on the live DB. Returns (rows, error)."""
        try:
            cur = self.conn.execute(sql)
            cols = [d[0] for d in cur.description] if cur.description else []
            rows = [dict(zip(cols, row)) for row in cur.fetchall()]
            return rows, None
        except sqlite3.Error as e:
            return None, str(e)

    def _handle_hint(self, payload: dict) -> dict:
        """Return schema info or sample rows — no reward, costs a step."""
        hint_type = payload.get("type", "schema")
        if hint_type == "schema":
            return {"hint_type": "schema", "content": SCHEMA_DDL}
        if hint_type == "sample_rows":
            table = payload.get("table", "songs")
            rows, error = self._execute_sql(f"SELECT * FROM {table} LIMIT 3")
            return {"hint_type": "sample_rows", "table": table, "rows": rows, "error": error}
        return {"error": f"Unknown hint type '{hint_type}'. Use 'schema' or 'sample_rows'."}

    def get_query_history(self) -> list[dict]:
        return self.query_history

    def get_task(self) -> TaskDef | None:
        return self.current_task
