"""
Base OpenEnv environment implementation.
Implements the standard step() / reset() / state() API.
"""
from abc import ABC, abstractmethod
from typing import Any
from pydantic import BaseModel


class StepResult(BaseModel):
    observation: dict[str, Any]
    reward: float
    done: bool
    info: dict[str, Any] = {}


class HackathonEnv(ABC):
    """
    Base class for the hackathon OpenEnv environment.
    TODO: Implement this with your chosen problem statement.
    """

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
