"""
OpenEnv-compliant FastAPI server.
Exposes all required endpoints: /reset, /step, /state, /tasks, /grader, /baseline
Plus extras: /health, /mcp, /leaderboard
"""
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

load_dotenv()

from src.environment.env import SQLQueryEnv, MAX_STEPS
from src.tasks import ALL_TASKS
from src.graders import rows_match, _partial_overlap
from src.graders.task_easy_grader import grader as easy_grader
from src.graders.task_medium_grader import grader as medium_grader
from src.graders.task_hard_grader import grader as hard_grader
from src.graders.task_analytics_grader import grader as analytics_grader
from src.graders.task_realtime_grader import grader as realtime_grader
from src.graders.task_expert_grader import grader as expert_grader
from src.graders.task_iterative_grader import grader as iterative_grader
from src.graders.task_adversarial_grader import grader as adversarial_grader
from src.baseline import run_baseline_on_env

# ---------------------------------------------------------------------------
# App + singletons
# ---------------------------------------------------------------------------

app = FastAPI(title="OpenEnv SQL Query Environment", version="1.0.0")

env = SQLQueryEnv()

# In-memory leaderboard — persists for the lifetime of the process
# Each entry: {model, mode, scores, avg_score, timestamp}
_LEADERBOARD: list[dict] = []

GRADERS = {
    "task_easy":      easy_grader,
    "task_medium":    medium_grader,
    "task_hard":      hard_grader,
    "task_analytics": analytics_grader,
    "task_realtime":  realtime_grader,
    "task_expert":      expert_grader,
    "task_iterative":   iterative_grader,
    "task_adversarial": adversarial_grader,
}

# ---------------------------------------------------------------------------
# Request models
# ---------------------------------------------------------------------------

class ResetRequest(BaseModel):
    task_id: str = "task_easy"


class Action(BaseModel):
    action_type: str = "query"
    payload: dict[str, Any] = {}


class MCPRequest(BaseModel):
    method: str
    params: dict[str, Any] = {}

# ---------------------------------------------------------------------------
# Required endpoints
# ---------------------------------------------------------------------------

@app.post("/reset")
def reset(body: ResetRequest = ResetRequest()):
    """Reset environment and return initial observation with schema + questions."""
    if body.task_id not in ALL_TASKS:
        raise HTTPException(status_code=400, detail=f"Unknown task_id '{body.task_id}'. Choose from: {list(ALL_TASKS)}")
    observation = env.reset(body.task_id)
    return {"status": "ok", "observation": observation}


@app.post("/step")
def step(action: Action):
    """Execute an action (SQL query or hint). Returns rows, reward, done."""
    result = env.step(action.model_dump())
    return result.model_dump()


@app.get("/state")
def state():
    """Get current environment state — task, step count, question list."""
    return env.state()


@app.get("/tasks")
def tasks():
    """List all tasks with full question details and action schema."""
    return {
        "tasks": [
            {
                "id":          task.id,
                "name":        task.name,
                "difficulty":  task.difficulty,
                "description": task.description,
                "questions": [
                    {"id": q.id, "text": q.text, "columns": q.columns}
                    for q in task.questions
                ],
                "action_schema": {
                    "query": {
                        "action_type": "query",
                        "payload": {"sql": "<SQL string>", "question_id": "<question id>"}
                    },
                    "hint": {
                        "action_type": "hint",
                        "payload": {"type": "schema | sample_rows", "table": "<table name (for sample_rows)>"}
                    },
                },
            }
            for task in ALL_TASKS.values()
        ]
    }


@app.get("/grader")
def grader(task_id: str = "task_easy"):
    """Return grader score for the current episode."""
    if task_id not in GRADERS:
        raise HTTPException(status_code=400, detail=f"Unknown task_id '{task_id}'")

    current_task = env.get_task()

    # Auto-reset to requested task if needed (ensures score is always available)
    if current_task is None or current_task.id != task_id:
        env.reset(task_id)

    score = GRADERS[task_id].grade(env.get_query_history())
    return {"task_id": task_id, "score": score}


@app.get("/episode_stats")
def episode_stats(task_id: str = "task_easy"):
    """
    Per-question breakdown for the current episode:
      - attempts: how many times the agent tried this question
      - best_score: highest score achieved (0.05 / 0.40 / 0.60 / 0.80 / 0.95)
      - solved: True if best_score >= 0.95
      - best_sql: the SQL that achieved best_score
    Also returns overall_score, steps_used, steps_remaining.
    """
    if task_id not in GRADERS:
        raise HTTPException(status_code=400, detail=f"Unknown task_id '{task_id}'")

    task    = ALL_TASKS[task_id]
    history = env.get_query_history()

    per_question: dict[str, dict] = {}
    for q in task.questions:
        attempts   = [e for e in history if e.get("question_id") == q.id]
        best_score = 0.0
        best_sql   = None

        for attempt in attempts:
            rows  = attempt.get("rows")
            error = attempt.get("error")

            if error or rows is None:
                score = 0.05
            else:
                matched, reason = rows_match(rows, q.expected_rows, q.order_sensitive)
                if matched:
                    score = 0.95
                elif reason == "correct_columns_wrong_values":
                    overlap = _partial_overlap(rows, q.expected_rows, q.order_sensitive)
                    score   = 0.80 if overlap >= 0.8 else 0.60 if overlap >= 0.5 else 0.40
                else:
                    score = 0.05

            if score > best_score:
                best_score = score
                best_sql   = attempt.get("sql")

        per_question[q.id] = {
            "attempts":   len(attempts),
            "best_score": best_score,
            "solved":     best_score >= 0.95,
            "best_sql":   best_sql,
        }

    overall = GRADERS[task_id].grade(history)
    return {
        "task_id":         task_id,
        "overall_score":   overall,
        "steps_used":      env.step_count,
        "steps_remaining": max(0, MAX_STEPS - env.step_count),
        "solved_count":    sum(1 for v in per_question.values() if v["solved"]),
        "questions":       per_question,
    }


@app.get("/baseline")
def baseline():
    """Run baseline policy on all tasks, return scores, and record on leaderboard."""
    use_llm = bool(
        os.environ.get("GROQ_API_KEY")
        or os.environ.get("OPENAI_API_KEY")
        or os.environ.get("API_KEY")
    )
    mode = "llm" if use_llm else "template"
    model = os.environ.get("MODEL_NAME", "llama-3.3-70b-versatile") if use_llm else "template-sql"
    scores = {}

    for task_id in ALL_TASKS:
        env.reset(task_id)
        run_baseline_on_env(env, task_id, mode="auto")
        scores[task_id] = GRADERS[task_id].grade(env.get_query_history())

    env.reset("task_easy")

    avg_score = round(sum(scores.values()) / len(scores), 4)

    # Record on leaderboard
    _LEADERBOARD.append({
        "model":     model,
        "mode":      mode,
        "scores":    scores,
        "avg_score": avg_score,
        "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    })
    # Keep only the best run per model
    seen: dict[str, dict] = {}
    for entry in _LEADERBOARD:
        m = entry["model"]
        if m not in seen or entry["avg_score"] > seen[m]["avg_score"]:
            seen[m] = entry
    _LEADERBOARD[:] = sorted(seen.values(), key=lambda e: e["avg_score"], reverse=True)

    return {"mode": mode, "model": model, "scores": scores, "avg_score": avg_score}


@app.get("/leaderboard")
def leaderboard():
    """
    In-memory leaderboard — best run per model, sorted by avg_score DESC.
    Updated automatically on every /baseline call.
    """
    ranked = [
        {
            "rank":      i + 1,
            "model":     e["model"],
            "mode":      e["mode"],
            "avg_score": e["avg_score"],
            "scores":    e["scores"],
            "timestamp": e["timestamp"],
        }
        for i, e in enumerate(_LEADERBOARD)
    ]
    return {"leaderboard": ranked, "entries": len(ranked)}

# ---------------------------------------------------------------------------
# Extra endpoints
# ---------------------------------------------------------------------------

@app.get("/ui", response_class=HTMLResponse)
def ui():
    """Interactive SQL playground UI."""
    html = (Path(__file__).parent.parent / "static" / "ui.html").read_text()
    return HTMLResponse(content=html)


@app.get("/health")
def health():
    """Liveness probe — verifies DB is live and seeded."""
    try:
        counts = {}
        for table in ("artists", "songs", "users", "streams", "playlists", "playlist_songs"):
            rows, _ = env._execute_sql(f"SELECT COUNT(*) AS n FROM {table}")
            counts[table] = rows[0]["n"] if rows else 0
        return {"status": "ok", "db_stats": counts}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/mcp")
def mcp(body: MCPRequest):
    """
    Model Context Protocol (JSON-RPC 2.0) endpoint.
    Supported methods: tools/list, tools/call
    """
    method = body.method
    params = body.params

    if method == "tools/list":
        return {
            "tools": [
                {
                    "name": "reset",
                    "description": "Reset the environment for a given task.",
                    "inputSchema": {"type": "object", "properties": {"task_id": {"type": "string"}}}
                },
                {
                    "name": "query",
                    "description": "Submit a SQL query for a specific question.",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "sql":         {"type": "string"},
                            "question_id": {"type": "string"},
                        },
                        "required": ["sql", "question_id"],
                    }
                },
                {
                    "name": "hint",
                    "description": "Request a schema hint or sample rows. Costs a step, no reward.",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "type":  {"type": "string", "enum": ["schema", "sample_rows"]},
                            "table": {"type": "string"},
                        },
                        "required": ["type"],
                    }
                },
                {
                    "name": "explain",
                    "description": "Run EXPLAIN QUERY PLAN on a SQL string. Returns the query plan without executing. Costs a step (reward 0.05) — use to verify complex queries before committing.",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "sql": {"type": "string"},
                        },
                        "required": ["sql"],
                    }
                },
            ]
        }

    if method == "tools/call":
        name = params.get("name")
        args = params.get("arguments", {})

        if name == "reset":
            task_id = args.get("task_id", "task_easy")
            obs = env.reset(task_id)
            return {"content": obs}

        if name == "query":
            result = env.step({"action_type": "query", "payload": args})
            return {"content": result.model_dump()}

        if name == "hint":
            result = env.step({"action_type": "hint", "payload": args})
            return {"content": result.model_dump()}

        if name == "explain":
            result = env.step({"action_type": "explain", "payload": args})
            return {"content": result.model_dump()}

        raise HTTPException(status_code=400, detail=f"Unknown tool '{name}'")

    raise HTTPException(status_code=400, detail=f"Unknown method '{method}'. Use 'tools/list' or 'tools/call'.")
