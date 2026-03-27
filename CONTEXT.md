# Session Context — Meta PyTorch OpenEnv Hackathon

Everything needed to pick up and continue this project from scratch.

---

## Competition

- **Hackathon:** Meta × PyTorch OpenEnv Hackathon x SST (Scaler School of Technology)
- **Dashboard:** https://www.scaler.com/school-of-technology/meta-pytorch-hackathon/dashboard
- **Round 1:** March 25 – April 5, 2026
- **Submission Deadline:** April 7, 2026, 11:59 PM IST
- **Finale (in-person, Bangalore):** April 25–26, 2026
- **Prize pool:** $30,000 | Top teams get Meta/HuggingFace interviews
- **Support:** help_openenvhackathon@scaler.com
- **Team:** Devesh B (solo)

---

## Links

| Resource | URL |
|----------|-----|
| GitHub repo (private) | https://github.com/DeveshB-1/meta-pytorch-openenv-hackathon |
| HuggingFace Space | https://huggingface.co/spaces/Dev176/openenv-sql-query-env |
| Interactive UI | https://huggingface.co/spaces/Dev176/openenv-sql-query-env/ui |
| HF Profile | https://huggingface.co/Dev176 |

---

## What We Built

**Tempo SQL Analytics Environment** — an OpenEnv-compliant environment where an AI agent writes SQL queries to answer natural language questions about Tempo, a music streaming analytics platform.

### Environment Summary
| | |
|---|---|
| **Action** | `{"action_type": "query", "payload": {"sql": "...", "question_id": "easy_q1"}}` |
| **Observation** | Query result rows, error, step count, task questions |
| **Reward** | correct=1.0, non-empty=0.05, error=-0.01, hint=0.0 |
| **Max steps** | 10 per episode |
| **Database** | In-memory SQLite: artists (25), songs (75), users (50), streams (419), playlists (35), playlist_songs (132) |

---

## Implementation Status — COMPLETE

| Step | File | Status |
|------|------|--------|
| 1 | `src/tasks/__init__.py` | ✅ DB + 15 questions with pre-computed expected answers |
| 2 | `src/graders/__init__.py` | ✅ BaseGrader, normalize_row, rows_match, SCORE_MAP |
| 3 | `src/graders/task_*_grader.py` | ✅ 3 thin subclasses, one per task |
| 4 | `src/environment/env.py` | ✅ SQLQueryEnv with reset/step/state/hints |
| 5 | `src/baseline.py` | ✅ Template SQL + Groq LLM mode (auto-detects API key) |
| 6 | `src/environment/server.py` | ✅ All endpoints wired + /health + /mcp + /ui |
| 7 | `src/static/ui.html` | ✅ Interactive SQL playground |
| 8 | `scripts/run_baseline.py` | ✅ HTTP client, scores 1.0 on all 3 tasks |
| 9 | `.github/workflows/deploy.yml` | ✅ Auto-deploy to HF Spaces on push to main |
| 10 | `openenv.yaml` + `README.md` | ✅ Updated with real descriptions |

---

## Repo Structure

```
meta-pytorch-openenv-hackathon/
├── PLAN.md                              ← original implementation plan
├── CONTEXT.md                           ← this file
├── README.md                            ← project docs + HF Space metadata
├── openenv.yaml                         ← OpenEnv spec config
├── Dockerfile                           ← python:3.11-slim, port 7860
├── requirements.txt                     ← all dependencies including groq
├── .github/
│   └── workflows/deploy.yml             ← auto-deploy to HF Spaces on push
├── src/
│   ├── environment/
│   │   ├── env.py                       ← HackathonEnv base + SQLQueryEnv
│   │   └── server.py                    ← FastAPI server, all endpoints
│   ├── tasks/
│   │   └── __init__.py                  ← DB creation + 15 Question objects
│   ├── graders/
│   │   ├── __init__.py                  ← BaseGrader + scoring logic
│   │   ├── task_easy_grader.py          ← grader singleton for task_easy
│   │   ├── task_medium_grader.py        ← grader singleton for task_medium
│   │   └── task_hard_grader.py          ← grader singleton for task_hard
│   ├── baseline.py                      ← template SQL + Groq LLM baseline
│   └── static/
│       └── ui.html                      ← interactive SQL playground UI
├── scripts/
│   ├── run_baseline.py                  ← HTTP client baseline runner
│   └── validate.py                      ← pre-submission validation (6 checks)
└── tests/
    └── __init__.py
```

---

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/reset` | POST | Reset env, returns schema + questions |
| `/step` | POST | Run SQL or hint, returns rows + reward |
| `/state` | GET | Task, step count, history count |
| `/tasks` | GET | All tasks with questions + action schema |
| `/grader` | GET | Episode score (0.0–1.0) |
| `/baseline` | GET | LLM/template baseline scores for all tasks |
| `/health` | GET | DB liveness + row counts |
| `/mcp` | POST | Model Context Protocol (tools/list, tools/call) |
| `/ui` | GET | Interactive browser playground |

---

## Differentiators

1. **Groq LLM Baseline** — Llama 3.3 70B writes SQL dynamically via Groq API, scores 1.0 on all tasks
2. **Hint Action** — agent can request schema DDL or sample rows (costs a step)
3. **MCP Endpoint** — JSON-RPC 2.0 protocol, any MCP-compatible client works out of the box
4. **Interactive UI** — `/ui` lets humans play the environment in a browser
5. **Intermediate Rewards** — per-step signals (not just final score) make env more RL-friendly
6. **Auto-deploy** — GitHub Actions pushes to HF Spaces on every commit

---

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `GROQ_API_KEY` | Optional | Enables Groq LLM baseline mode |
| `HF_TOKEN` | CI only | Used by GitHub Actions to push to HF Spaces |

Saved in: `~/.bashrc`, `~/.config/fish/config.fish`, `.env` (local), GitHub Secrets, HF Space Secrets.

---

## Local Development

```bash
# Install deps
pip install -r requirements.txt

# Start server with auto-reload
uvicorn src.environment.server:app --host 0.0.0.0 --port 8000 --reload

# Open UI
open http://localhost:8000/ui

# Run validation
python scripts/validate.py

# Run baseline (uses Groq if GROQ_API_KEY set)
python scripts/run_baseline.py

# Docker
docker build -t openenv-sql . && docker run -p 7860:7860 openenv-sql
```

---

## Key Gotchas

- Pydantic v2: use `.model_dump()` not `.dict()`
- SQLite window functions need SQLite 3.25+ — python:3.11-slim ships 3.39 ✓
- `sqlite3.connect(":memory:", check_same_thread=False)` for thread safety
- HF Spaces uses port 7860 (Dockerfile updated)
- `/baseline` resets env after running — always leaves env in `task_easy`
- Column aliases in SQL must match `question.columns` exactly for grader to score correctly
- Expected answers are pre-computed at module load using a reference DB (`_ref` in tasks/__init__.py)
- All ORDER BY clauses have deterministic tiebreakers (e.g., `ORDER BY stream_count DESC, s.title ASC`) — required for SQLite to produce stable ordering across multiple DB instances
- When GROQ_API_KEY is set, run_baseline.py uses LLM mode (Groq Llama 3.3 70B) which may not add tiebreakers — template mode (`GROQ_API_KEY=""`) always scores 1.0

---

## Submission Checklist

- [x] HF Space deployed and live
- [x] `/reset` responds correctly
- [x] OpenEnv spec compliant (`openenv.yaml`, typed Pydantic models)
- [x] Dockerfile builds and runs on port 7860
- [x] Baseline script runs without error, scores 1.0
- [x] 3 tasks with graders (scores 0.0–1.0)
- [ ] Submit HF Space URL to Scaler dashboard before April 7, 2026 11:59 PM IST
