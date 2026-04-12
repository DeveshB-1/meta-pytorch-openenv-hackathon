"""
Pydantic models for the Tempo SQL Analytics OpenEnv environment.
Re-exported from src for convenience and validator compliance.
"""
from typing import Any
from pydantic import BaseModel


class ResetRequest(BaseModel):
    task_id: str = "task_easy"


class Action(BaseModel):
    action_type: str = "query"
    payload: dict[str, Any] = {}


class StepResult(BaseModel):
    observation: dict[str, Any]
    reward: float
    done: bool
    info: dict[str, Any] = {}


class TaskInfo(BaseModel):
    id: str
    name: str
    difficulty: str
    description: str
    n_questions: int


class EnvironmentMetadata(BaseModel):
    name: str
    version: str
    author: str
    description: str
    spec_version: int
    reward_range: list[float]
    max_steps: int


__all__ = [
    "ResetRequest",
    "Action",
    "StepResult",
    "TaskInfo",
    "EnvironmentMetadata",
]
