"""
HTTP client for the Tempo SQL Analytics OpenEnv environment.

Usage:
    from client import TempoEnvClient

    client = TempoEnvClient("http://localhost:7860")
    obs    = client.reset("task_easy")
    result = client.query(sql="SELECT COUNT(*) FROM songs", question_id="easy_q1")
    score  = client.grader("task_easy")
"""
from __future__ import annotations

import httpx
from typing import Any


class TempoEnvClient:
    """Synchronous HTTP client wrapping the Tempo SQL Analytics REST API."""

    def __init__(self, base_url: str = "http://localhost:7860", timeout: float = 30.0):
        self.base_url = base_url.rstrip("/")
        self._client = httpx.Client(base_url=self.base_url, timeout=timeout)

    # ------------------------------------------------------------------
    # Core OpenEnv endpoints
    # ------------------------------------------------------------------

    def reset(self, task_id: str = "task_easy") -> dict[str, Any]:
        """Reset the environment and return the initial observation."""
        resp = self._client.post("/reset", json={"task_id": task_id})
        resp.raise_for_status()
        return resp.json()["observation"]

    def step(self, action_type: str, payload: dict[str, Any]) -> dict[str, Any]:
        """Execute an action and return (observation, reward, done, info)."""
        resp = self._client.post("/step", json={"action_type": action_type, "payload": payload})
        resp.raise_for_status()
        return resp.json()

    def state(self) -> dict[str, Any]:
        """Return current environment state."""
        resp = self._client.get("/state")
        resp.raise_for_status()
        return resp.json()

    # ------------------------------------------------------------------
    # Convenience wrappers
    # ------------------------------------------------------------------

    def query(self, sql: str, question_id: str) -> dict[str, Any]:
        """Submit a SQL query for a specific question."""
        return self.step("query", {"sql": sql, "question_id": question_id})

    def hint(self, hint_type: str, table: str | None = None) -> dict[str, Any]:
        """Request a schema hint or sample rows (costs a step)."""
        payload: dict[str, Any] = {"type": hint_type}
        if table:
            payload["table"] = table
        return self.step("hint", payload)

    def explain(self, sql: str) -> dict[str, Any]:
        """Run EXPLAIN QUERY PLAN on a SQL string without executing it."""
        return self.step("explain", {"sql": sql})

    # ------------------------------------------------------------------
    # Info endpoints
    # ------------------------------------------------------------------

    def tasks(self) -> list[dict[str, Any]]:
        """List all available tasks."""
        resp = self._client.get("/tasks")
        resp.raise_for_status()
        return resp.json()["tasks"]

    def grader(self, task_id: str = "task_easy") -> float:
        """Return the graded score for the current episode."""
        resp = self._client.get("/grader", params={"task_id": task_id})
        resp.raise_for_status()
        return resp.json()["score"]

    def episode_stats(self, task_id: str = "task_easy") -> dict[str, Any]:
        """Return per-question stats: attempts, best_score, solved, best_sql."""
        resp = self._client.get("/episode_stats", params={"task_id": task_id})
        resp.raise_for_status()
        return resp.json()

    def metadata(self) -> dict[str, Any]:
        """Return environment metadata (name, version, author, description)."""
        resp = self._client.get("/metadata")
        resp.raise_for_status()
        return resp.json()

    def health(self) -> dict[str, Any]:
        """Liveness probe — returns status and row counts per table."""
        resp = self._client.get("/health")
        resp.raise_for_status()
        return resp.json()

    # ------------------------------------------------------------------
    # MCP (Model Context Protocol)
    # ------------------------------------------------------------------

    def mcp_tools(self) -> list[dict[str, Any]]:
        """List available MCP tools."""
        resp = self._client.post("/mcp", json={"method": "tools/list"})
        resp.raise_for_status()
        return resp.json()["tools"]

    def mcp_call(self, tool_name: str, arguments: dict[str, Any]) -> Any:
        """Call an MCP tool by name."""
        resp = self._client.post(
            "/mcp",
            json={"method": "tools/call", "params": {"name": tool_name, "arguments": arguments}},
        )
        resp.raise_for_status()
        return resp.json()["content"]

    def close(self):
        self._client.close()

    def __enter__(self):
        return self

    def __exit__(self, *_):
        self.close()
