"""
OpenEnv-compliant FastAPI server.
Exposes all required endpoints: /reset, /step, /state, /tasks, /grader, /baseline
"""
from fastapi import FastAPI
from pydantic import BaseModel
from typing import Any

app = FastAPI(title="OpenEnv Hackathon", version="1.0.0")

# TODO: Import and instantiate your environment
# from src.environment.env import YourEnv
# env = YourEnv()


class Action(BaseModel):
    action_type: str
    payload: dict[str, Any] = {}


@app.post("/reset")
def reset():
    """Reset environment and return initial observation."""
    # return env.reset()
    return {"status": "ok", "observation": {}}


@app.post("/step")
def step(action: Action):
    """Execute an action and return next state, reward, done."""
    # return env.step(action.dict())
    return {"observation": {}, "reward": 0.0, "done": False, "info": {}}


@app.get("/state")
def state():
    """Get current environment state."""
    # return env.state()
    return {}


@app.get("/tasks")
def tasks():
    """List all tasks and their action schemas."""
    return {
        "tasks": [
            {"id": "task_easy",   "difficulty": "easy",   "action_schema": {}},
            {"id": "task_medium", "difficulty": "medium", "action_schema": {}},
            {"id": "task_hard",   "difficulty": "hard",   "action_schema": {}},
        ]
    }


@app.get("/grader")
def grader(task_id: str = "task_easy"):
    """Return grader score for a completed episode."""
    # TODO: Implement grader logic
    return {"task_id": task_id, "score": 0.0}


@app.get("/baseline")
def baseline():
    """Run baseline inference and return scores for all tasks."""
    # TODO: Run actual baseline
    return {
        "scores": {
            "task_easy":   0.0,
            "task_medium": 0.0,
            "task_hard":   0.0,
        }
    }
