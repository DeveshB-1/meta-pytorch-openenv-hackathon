"""
OpenEnv-compliant FastAPI server.
Exposes all required endpoints: /reset, /step, /state, /tasks, /grader, /baseline
Plus extras: /health, /mcp
"""
import os
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

load_dotenv()

from src.environment.env import SQLQueryEnv
from src.tasks import ALL_TASKS
from src.graders.task_easy_grader import grader as easy_grader
from src.graders.task_medium_grader import grader as medium_grader
from src.graders.task_hard_grader import grader as hard_grader
from src.graders.task_analytics_grader import grader as analytics_grader
from src.graders.task_realtime_grader import grader as realtime_grader
from src.baseline import run_baseline_on_env

# ---------------------------------------------------------------------------
# App + singletons
# ---------------------------------------------------------------------------

app = FastAPI(title="OpenEnv SQL Query Environment", version="1.0.0")

env = SQLQueryEnv()

GRADERS = {
    "task_easy":      easy_grader,
    "task_medium":    medium_grader,
    "task_hard":      hard_grader,
    "task_analytics": analytics_grader,
    "task_realtime":  realtime_grader,
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


@app.get("/baseline")
def baseline():
    """Run baseline policy on all 3 tasks and return scores."""
    mode = "auto"  # uses Groq if GROQ_API_KEY set, else template
    scores = {}

    for task_id in ALL_TASKS:
        env.reset(task_id)
        run_baseline_on_env(env, task_id, mode=mode)
        scores[task_id] = GRADERS[task_id].grade(env.get_query_history())

    # Reset env back to easy so it's in a clean state
    env.reset("task_easy")

    return {
        "mode":   "llm" if (os.environ.get("OPENAI_API_KEY") or os.environ.get("API_KEY")) else "template",
        "scores": scores,
    }

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

        raise HTTPException(status_code=400, detail=f"Unknown tool '{name}'")

    raise HTTPException(status_code=400, detail=f"Unknown method '{method}'. Use 'tools/list' or 'tools/call'.")
