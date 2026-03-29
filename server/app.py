"""
OpenEnv server entry point.
Re-exports the FastAPI app from src.environment.server and provides
a main() entry point for [project.scripts].
"""
import uvicorn
from src.environment.server import app  # noqa: F401


def main():
    """Entry point for `server` script."""
    uvicorn.run("server.app:app", host="0.0.0.0", port=7860)


if __name__ == "__main__":
    main()
