---
title: Tempo — Music Streaming Analytics Environment
emoji: 🎵
colorFrom: purple
colorTo: indigo
sdk: docker
app_port: 7860
pinned: false
---

# Tempo — Music Streaming Analytics Environment

[![Live Space](https://img.shields.io/badge/🤗-Live%20Space-blue)](https://huggingface.co/spaces/Dev176/openenv-sql-query-env)
[![GitHub](https://img.shields.io/badge/GitHub-DeveshB--1-black?logo=github)](https://github.com/DeveshB-1/meta-pytorch-openenv-hackathon)
[![OpenEnv](https://img.shields.io/badge/OpenEnv-compliant-green)](https://github.com/huggingface/openenv)

> Built for the **Meta × PyTorch OpenEnv Hackathon x SST 2026**

An [OpenEnv](https://github.com/huggingface/openenv)-compliant RL environment where an AI agent writes SQL queries to answer natural-language analytics questions about **Tempo** — a music streaming platform with rich behavioural data: skip events, completion rates, discovery sources, and playlist graphs.

**Live:** https://huggingface.co/spaces/Dev176/openenv-sql-query-env
**Interactive playground:** https://huggingface.co/spaces/Dev176/openenv-sql-query-env/ui

---

## What is Tempo?

Tempo is a music streaming platform with 6 normalised tables. Every stream record captures *how* a user discovered a song (search / recommendation / playlist / radio / artist page), whether they completed it, and exactly where they skipped — making it uniquely suited for behavioural analytics and agent training.

### Database

| Table | Rows | Key columns |
|-------|------|-------------|
| `artists` | 30 | id, name, country, debut_year, monthly_listeners, genre |
| `songs` | 110 | id, title, artist_id, genre, bpm, mood, duration_sec, release_year |
| `users` | 75 | id, username, country, subscription_tier, joined_year, age |
| `streams` | 650 | id, user_id, song_id, played_at, completed, skipped_at_sec, source |
| `playlists` | 50 | id, name, user_id, is_public, created_at |
| `playlist_songs` | 199 | playlist_id, song_id, position, added_at |

30 artists across 15 countries and 15+ genres — Electronic, K-Pop, Afrobeats, Lo-fi Hip-hop, Jazz Fusion, Bollywood Fusion, Latin, Indie Rock, Metal, Synth-pop, Nordic Folk Electronic, and more.

---

## Environment

Each episode presents **5 natural-language analytics questions** at a chosen difficulty. The agent submits SQL queries and receives rewards based on correctness. Goal: perfect episode score of 1.0.

### Reward Structure

| Outcome | Reward |
|---------|--------|
| Correct answer (exact match) | `+1.0` |
| Non-empty result (partial progress) | `+0.05` |
| SQL error | `-0.01` |
| Hint action | `0.0` |

---

## Tasks

| Task | Difficulty | SQL Type | Example question |
|------|-----------|----------|-----------------|
| `task_easy` | Easy | Single-table SELECT, WHERE, GROUP BY | "List all songs in the Electronic genre" |
| `task_medium` | Medium | JOINs, multi-table aggregations | "What are the top 10 most streamed songs?" |
| `task_hard` | Hard | Window functions, CTEs, subqueries | "Rank songs by stream count within their genre" |

Scoring: average of best-attempt-per-question across all 5 questions in the task.

---

## Action & Observation Spaces

### Actions

**Submit a SQL query:**
```json
{
  "action_type": "query",
  "payload": {
    "sql": "SELECT title, genre FROM songs WHERE mood = 'Energetic'",
    "question_id": "easy_q1"
  }
}
```

**Request a hint (costs a step, no reward):**
```json
{ "action_type": "hint", "payload": { "type": "schema" } }
{ "action_type": "hint", "payload": { "type": "sample_rows", "table": "streams" } }
```

### Observation
```json
{
  "task_id": "task_easy",
  "question_id": "easy_q1",
  "rows": [{"id": 1, "title": "Pulse Override", "genre": "Electronic", "bpm": 128}],
  "error": null,
  "step": 1,
  "max_steps": 10
}
```

---

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/reset` | POST | Start episode — returns schema DDL + questions |
| `/step` | POST | Execute SQL or hint — returns rows + reward |
| `/state` | GET | Current task, step count, history |
| `/tasks` | GET | All tasks with questions and action schema |
| `/grader` | GET | Episode score (0.0–1.0) |
| `/baseline` | GET | Run baseline agent, return scores for all tasks |
| `/health` | GET | Liveness probe with DB row counts |
| `/mcp` | POST | Model Context Protocol JSON-RPC 2.0 |
| `/ui` | GET | Interactive SQL playground |

---

## MCP Support

The `/mcp` endpoint implements [Model Context Protocol](https://modelcontextprotocol.io) (JSON-RPC 2.0) — any MCP-compatible AI client can auto-discover and use the environment with no custom integration.

```bash
curl -X POST https://dev176-openenv-sql-query-env.hf.space/mcp \
  -H "Content-Type: application/json" \
  -d '{"method": "tools/list"}'
# Returns: reset, query, hint tools with full schemas
```

---

## Baseline & Inference

`inference.py` runs all 3 tasks using the OpenAI client. Set `API_BASE_URL` + `MODEL_NAME` + `OPENAI_API_KEY` for LLM mode; falls back to template SQL (scores 1.0) if no key is set.

```bash
# Template mode (always 1.0)
python inference.py

# LLM mode
API_BASE_URL=https://api.groq.com/openai/v1 \
MODEL_NAME=llama-3.3-70b-versatile \
OPENAI_API_KEY=your_key \
python inference.py
```

```bash
curl https://dev176-openenv-sql-query-env.hf.space/baseline
# {"mode": "template", "scores": {"task_easy": 1.0, "task_medium": 1.0, "task_hard": 1.0}}
```

---

## Quick Example

```python
import httpx

BASE = "https://dev176-openenv-sql-query-env.hf.space"

# Start a hard episode
obs = httpx.post(f"{BASE}/reset", json={"task_id": "task_hard"}).json()
print(obs["observation"]["questions"][0]["text"])
# "Rank songs by stream count within their genre using a window function..."

# Submit SQL
result = httpx.post(f"{BASE}/step", json={
    "action_type": "query",
    "payload": {
        "sql": """
            WITH song_streams AS (
                SELECT song_id, COUNT(*) AS stream_count FROM streams GROUP BY song_id
            ),
            avg_streams AS (SELECT AVG(stream_count) AS avg_count FROM song_streams)
            SELECT s.title, s.genre, ss.stream_count
            FROM songs s JOIN song_streams ss ON s.id = ss.song_id
            WHERE ss.stream_count > (SELECT avg_count FROM avg_streams)
            ORDER BY ss.stream_count DESC, s.title ASC
        """,
        "question_id": "hard_q3"
    }
}).json()
print(result["reward"])  # 1.0

# Get episode score
score = httpx.get(f"{BASE}/grader", params={"task_id": "task_hard"}).json()
print(score["score"])  # 0.0–1.0
```

---

## Setup

```bash
git clone https://github.com/DeveshB-1/meta-pytorch-openenv-hackathon.git
cd meta-pytorch-openenv-hackathon
pip install -r requirements.txt

# Start server
uvicorn src.environment.server:app --host 0.0.0.0 --port 8000 --reload

# Open UI
open http://localhost:8000/ui

# Run inference
python inference.py

# Validate
python scripts/validate.py
```

## Docker

```bash
docker build -t tempo-openenv .
docker run -p 7860:7860 tempo-openenv
```

---

## Why This Environment is Interesting for RL

- **Rich behavioural schema** — skip timestamps, completion flags, and source labels enable queries that reflect real recommendation-engine analytics
- **Intermediate rewards** — `+0.05` on any non-empty result gives gradient signal before finding the exact answer
- **Hint action** — agent can request schema or sample rows mid-episode, at the cost of a step
- **10 steps per episode** — agent can refine queries across multiple attempts
- **Three difficulty tiers** — single-table → multi-join → window functions/CTEs
- **MCP endpoint** — plug any MCP-compatible agent in without glue code

---

## What Makes This Stand Out

- **Real-world domain** — music streaming analytics with skip patterns, discovery sources, and completion rates; not a toy or game
- **Full OpenEnv compliance** — `openenv.yaml`, typed Pydantic models, `step()`/`reset()`/`state()` API, `inference.py`, `pyproject.toml`
- **LLM baseline using OpenAI client** — `API_BASE_URL` + `MODEL_NAME` configurable at runtime
- **Interactive UI** — `/ui` lets humans explore the environment in a browser
- **MCP protocol** — JSON-RPC 2.0 tool discovery out of the box
- **Auto-deploy** — GitHub Actions pushes to HF Spaces on every commit

---

## Author

**Devesh B** — Solo submission, Meta × PyTorch OpenEnv Hackathon x SST 2026

- GitHub: [DeveshB-1](https://github.com/DeveshB-1)
- HuggingFace: [Dev176](https://huggingface.co/Dev176)

---

## License

MIT
