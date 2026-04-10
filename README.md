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
| Correct answer (exact row match) | `+0.95` |
| High partial match (≥ 80 % rows correct) | `+0.80` |
| Medium partial match (≥ 50 % rows correct) | `+0.60` |
| Correct columns, < 50 % rows match | `+0.40` |
| Non-empty result (wrong structure) | `+0.10` |
| SQL error / hint / explain | `+0.05` |

The grader uses **partial row credit** — if an agent gets the right schema and most rows correct, it earns meaningful reward even without an exact answer. This produces denser gradient signal for RL training.

---

## Tasks

| Task | Difficulty | SQL Type | Example question |
|------|-----------|----------|-----------------|
| `task_easy` | Easy | Single-table SELECT, WHERE, GROUP BY | "List all songs in the Electronic genre" |
| `task_medium` | Medium | JOINs, multi-table aggregations | "What are the top 10 most streamed songs?" |
| `task_hard` | Hard | Window functions, CTEs, subqueries | "Rank songs by stream count within their genre" |
| `task_analytics` | Analytics | Revenue proxies, engagement rates, cross-tabulations | "Revenue proxy per genre (premium=2, free=1)" |
| `task_realtime` | Realtime | Time-series, MoM growth, trend analysis | "Monthly skip-rate trend across all streams" |
| `task_expert` | Expert | All 6 tables, playlist attribution, penetration rates | "Artist listener penetration % across all users" |
| `task_iterative` | Iterative | Running totals, per-user rankings, LEFT JOIN edge cases | "Each user's most-streamed genre using RANK()" |

**35 questions total** across 7 difficulty tiers. Scores are strictly in (0, 1) — partial credit always awarded.

### Calibration

Template baseline = hardcoded correct SQL. Theoretical max = 0.9499 (all 5 questions exact). Partial credit kicks in below that.

| Task | Template baseline | Theoretical max | What makes it hard |
|------|:-----------------:|:---------------:|---------------------|
| `task_easy` | 0.95 | 0.95 | — straightforward single-table |
| `task_medium` | 0.84 | 0.95 | JOIN + correct alias ordering |
| `task_hard` | 0.77 | 0.95 | Window functions, RANK(), CTEs |
| `task_analytics` | 0.84 | 0.95 | Revenue proxy formula, HAVING filter |
| `task_realtime` | 0.84 | 0.95 | Date slicing, MoM COALESCE |
| `task_expert` | 0.63 | 0.95 | All 6 tables, LEFT JOIN attribution |
| `task_iterative` | 0.81 | 0.95 | LEFT JOIN IS NULL traps, RANK() OVER |

> Template scores below 0.95 mean the reference queries produce equivalent-but-not-byte-identical output (e.g. floating-point rounding differences across SQLite builds) — the partial credit grader captures these correctly. Run `python inference.py` with `HF_TOKEN` set to measure LLM performance.

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

**Request a hint (costs a step, +0.05 reward):**
```json
{ "action_type": "hint", "payload": { "type": "schema" } }
{ "action_type": "hint", "payload": { "type": "sample_rows", "table": "streams" } }
```

**Explain a query before committing (costs a step, +0.05 reward):**
```json
{ "action_type": "explain", "payload": { "sql": "SELECT ..." } }
```
Returns `EXPLAIN QUERY PLAN` output — lets the agent verify join strategy and index usage before spending a step on the actual query.

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
| `/step` | POST | Execute SQL, hint, or explain — returns rows + reward |
| `/state` | GET | Current task, step count, history |
| `/tasks` | GET | All tasks with questions and action schema |
| `/grader` | GET | Episode score (0.0–1.0) |
| `/baseline` | GET | Run baseline agent, return scores for all tasks + update leaderboard |
| `/leaderboard` | GET | Best run per model, sorted by avg score — auto-updated by `/baseline` |
| `/health` | GET | Liveness probe with DB row counts |
| `/mcp` | POST | Model Context Protocol JSON-RPC 2.0 |
| `/ui` | GET | Interactive SQL playground |

---

## MCP Support

The `/mcp` endpoint implements [Model Context Protocol](https://modelcontextprotocol.io) (JSON-RPC 2.0) — any MCP-compatible AI client can auto-discover and use the environment with no custom integration.

Four tools exposed: `reset`, `query`, `hint`, `explain`.

```bash
curl -X POST https://dev176-openenv-sql-query-env.hf.space/mcp \
  -H "Content-Type: application/json" \
  -d '{"method": "tools/list"}'
# Returns: reset, query, hint, explain tools with full schemas
```

---

## Baseline & Inference

`inference.py` runs all 7 tasks using the OpenAI-compatible client. Set `API_BASE_URL` + `MODEL_NAME` + `HF_TOKEN` for LLM mode; falls back to template SQL if no key is set. Outputs structured `[START]`/`[STEP]`/`[END]` logs.

```bash
# Template mode
python inference.py

# LLM mode (Groq)
API_BASE_URL=https://api.groq.com/openai/v1 \
MODEL_NAME=llama-3.3-70b-versatile \
HF_TOKEN=your_key \
python inference.py
```

Example output:
```
[START] task=task_easy env=tempo-sql-analytics-env model=llama-3.3-70b-versatile
[STEP] step=1 action={"action_type":"query",...} reward=0.95 done=false error=null
...
[END] success=true steps=5 score=0.950 rewards=0.95,0.95,0.95,0.95,0.95
```

```bash
curl https://dev176-openenv-sql-query-env.hf.space/baseline
# {"mode": "template", "scores": {"task_easy": 0.95, "task_medium": 0.95, ...}}
```

---

## Quick Example

```python
import httpx

BASE = "https://dev176-openenv-sql-query-env.hf.space"

# Start an expert episode
obs = httpx.post(f"{BASE}/reset", json={"task_id": "task_expert"}).json()
print(obs["observation"]["questions"][0]["text"])
# "For each public playlist, count its songs and how many streams came from source='playlist'..."

# Explain your query plan before committing
plan = httpx.post(f"{BASE}/step", json={
    "action_type": "explain",
    "payload": {
        "sql": "SELECT p.name, COUNT(st.id) FROM playlists p JOIN playlist_songs ps ON p.id=ps.playlist_id LEFT JOIN streams st ON ps.song_id=st.song_id AND st.source='playlist' WHERE p.is_public=1 GROUP BY p.id"
    }
}).json()
print(plan["observation"]["plan"])  # ["SCAN playlists p", "SEARCH playlist_songs ...", ...]

# Submit the query for real
result = httpx.post(f"{BASE}/step", json={
    "action_type": "query",
    "payload": {
        "sql": """
            SELECT p.name AS playlist_name, u.username AS owner_username,
                   COUNT(DISTINCT ps.song_id) AS songs_in_playlist,
                   COUNT(st.id) AS playlist_streams
            FROM playlists p
            JOIN users u ON p.user_id = u.id
            JOIN playlist_songs ps ON p.id = ps.playlist_id
            LEFT JOIN streams st ON ps.song_id = st.song_id AND st.source = 'playlist'
            WHERE p.is_public = 1
            GROUP BY p.id, p.name, u.username
            ORDER BY playlist_streams DESC, p.name ASC
        """,
        "question_id": "expert_q1"
    }
}).json()
print(result["reward"])  # 0.95

# Get episode score
score = httpx.get(f"{BASE}/grader", params={"task_id": "task_expert"}).json()
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

# Run tests (25 tests)
python -m pytest tests/ -v

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
- **Partial row credit** — grader awards 0.80/0.60/0.40 based on row overlap %, giving continuous gradient signal instead of binary correct/wrong
- **Intermediate step rewards** — `+0.05` on any non-empty result; `+0.10` on a non-empty correct-schema result
- **Explain action** — agent can run `EXPLAIN QUERY PLAN` before committing, creating a cost/benefit tradeoff for query inspection
- **Hint action** — request schema or sample rows mid-episode, at the cost of a step
- **10 steps per episode** — agent can refine queries across multiple attempts
- **Seven difficulty tiers** — single-table → joins → window functions → full-database → iterative refinement
- **MCP endpoint** — plug any MCP-compatible agent in without glue code

---

## What Makes This Stand Out

- **Real-world domain** — music streaming analytics with skip patterns, discovery sources, and completion rates; not a toy or game
- **Full OpenEnv compliance** — `openenv.yaml`, typed Pydantic models, `step()`/`reset()`/`state()` API, `inference.py`, `pyproject.toml`
- **Partial row credit grader** — dense reward signal for RL training; intermediate rewards at 0.40, 0.60, and 0.80 before reaching 0.95
- **`/explain` action** — unique to this environment; lets agents inspect query plans before submitting
- **`/leaderboard` endpoint** — in-memory benchmark leaderboard, best-run-per-model sorted by avg score, auto-populated by `/baseline`
- **LLM baseline using OpenAI client** — `API_BASE_URL` + `MODEL_NAME` configurable at runtime
- **Interactive UI** — `/ui` lets humans explore the environment in a browser
- **MCP protocol** — JSON-RPC 2.0 tool discovery out of the box with 4 tools
- **Auto-deploy** — GitHub Actions pushes to HF Spaces on every commit
- **25 pytest tests** — covers all 7 tasks, partial scoring, explain action, and DB integrity

---

## Author

**Devesh B** — Solo submission, Meta × PyTorch OpenEnv Hackathon x SST 2026

- GitHub: [DeveshB-1](https://github.com/DeveshB-1)
- HuggingFace: [Dev176](https://huggingface.co/Dev176)

---

## License

MIT
