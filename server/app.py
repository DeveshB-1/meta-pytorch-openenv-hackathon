"""
OpenEnv server entry point.
Re-exports the FastAPI app from src.environment.server and provides
a CLI-compatible start() function for [project.scripts].
"""
import uvicorn
from src.environment.server import app  # noqa: F401


def start():
    """Entry point for `openenv-server` script."""
    uvicorn.run("server.app:app", host="0.0.0.0", port=7860)
