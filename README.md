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

[![Deploy to HuggingFace Spaces](https://huggingface.co/datasets/huggingface/badges/resolve/main/deploy-to-spaces-sm.svg)](https://huggingface.co/new-space?template=Dev176/openenv-sql-query-env)
[![Live Space](https://img.shields.io/badge/🤗-Live%20Space-blue)](https://huggingface.co/spaces/Dev176/openenv-sql-query-env)
[![GitHub](https://img.shields.io/badge/GitHub-DeveshB--1-black?logo=github)](https://github.com/DeveshB-1/meta-pytorch-openenv-hackathon)

> Built for the **Meta × PyTorch OpenEnv Hackathon x SST 2026** — India's Biggest MEGA AI Hackathon.

An [OpenEnv](https://github.com/huggingface/openenv)-compliant RL environment where an AI agent writes SQL queries to answer natural-language analytics questions about **Tempo** — a fictional music streaming platform with rich behavioural data: skip events, completion rates, discovery sources, playlist graphs, and more.

**Try it live:** https://huggingface.co/spaces/Dev176/openenv-sql-query-env
**Interactive UI:** https://huggingface.co/spaces/Dev176/openenv-sql-query-env/ui

---

## What is Tempo?

Tempo is a music streaming platform database with 6 normalised tables covering artists, songs, listeners, stream events, and playlists. Every stream record captures *how* a user found a song (search / recommendation / playlist / radio / artist page), whether they finished it, and exactly where they skipped — making the data uniquely suited for behavioural analytics and RL agent training.

### Database at a glance

| Table | Rows | Key columns |
|-------|------|-------------|
| `artists` | 25 | id, name, country, debut_year, monthly_listeners, genre |
| `songs` | 75 | id, title, artist_id, genre, bpm, mood, duration_sec, release_year |
| `users` | 50 | id, username, country, subscription_tier, joined_year, age |
| `streams` | 419 | id, user_id, song_id, played_at, completed, skipped_at_sec, source |
| `playlists` | 35 | id, name, user_id, is_public, created_at |
| `playlist_songs` | 132 | playlist_id, song_id, position, added_at |

Artists span 15 countries (USA, UK, Japan, South Korea, Brazil, India, Nigeria, Germany, Norway, France, Mexico, Australia, South Africa, Canada, Spain) across 15+ genres — Electronic, K-Pop, J-Pop, Afrobeats, Lo-fi Hip-hop, Jazz Fusion, Bollywood Fusion, Latin, Indie Rock, Metal, Synth-pop, Ambient, Nordic Folk Electronic, Techno, R&B Pop, and more.

---

## Environment Description

Each episode presents **5 natural-language analytics questions** at a chosen difficulty level. The agent submits SQL queries and receives rewards based on correctness. The goal is a perfect episode score of 1.0.

### Reward Structure

| Outcome | Reward |
|---------|--------|
| Correct answer (exact match) | `1.0` |
| Non-empty result (wrong answer) | `0.05` |
| SQL error | `-0.01` |
| Hint action | `0.0` |

---

## Tasks

| Task ID | Difficulty | Type | Sample question |
|---------|-----------|------|-----------------|
| `task_easy` | Easy | Single-table SELECT, WHERE, GROUP BY | "List all songs in the 'Electronic' genre" |
| `task_medium` | Medium | JOINs, multi-table aggregations | "What are the top 10 most streamed songs?" |
| `task_hard` | Hard | Window functions, CTEs, subqueries | "Rank songs by stream count within their genre" |

**Scoring:** average of best-attempt-per-question across all 5 questions.

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
```
```json
{ "action_type": "hint", "payload": { "type": "sample_rows", "table": "streams" } }
```

### Observation
```json
{
  "task_id": "task_easy",
  "question_id": "easy_q1",
  "rows": [
    {"id": 1, "title": "Pulse Override", "genre": "Electronic", "bpm": 128, "mood": "Energetic"}
  ],
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
| `/step` | POST | Execute SQL query or hint — returns rows + reward |
| `/state` | GET | Current task, step count, history count |
| `/tasks` | GET | All tasks with questions and action schema |
| `/grader` | GET | Episode score (0.0–1.0) |
| `/baseline` | GET | Run LLM/template baseline, return scores for all tasks |
| `/health` | GET | Liveness probe with DB row counts |
| `/mcp` | POST | Model Context Protocol JSON-RPC 2.0 |
| `/ui` | GET | Interactive SQL playground in-browser |

---

## MCP Support

The `/mcp` endpoint implements [Model Context Protocol](https://modelcontextprotocol.io) (JSON-RPC 2.0), so any MCP-compatible AI client can auto-discover and use the environment with no custom integration.

```bash
# Discover available tools
curl -X POST https://dev176-openenv-sql-query-env.hf.space/mcp \
  -H "Content-Type: application/json" \
  -d '{"method": "tools/list"}'

# Use a tool
curl -X POST https://dev176-openenv-sql-query-env.hf.space/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "method": "tools/call",
    "params": {
      "name": "query",
      "arguments": {
        "sql": "SELECT title, COUNT(*) AS stream_count FROM songs JOIN streams ON songs.id = streams.song_id GROUP BY songs.id ORDER BY stream_count DESC LIMIT 5",
        "question_id": "medium_q1"
      }
    }
  }'
```

Available tools: `reset`, `query`, `hint`

---

## LLM Baseline

When `GROQ_API_KEY` is set, `/baseline` uses **Llama 3.3 70B** (via Groq) to write SQL dynamically from just the schema DDL and question text — no hardcoded answers. The template baseline always scores 1.0 on all 3 tasks.

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

# Submit SQL with a CTE
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
print(result["reward"])  # 1.0 if correct
print(result["observation"]["rows"][:3])

# Check skip rates per artist (hard_q4)
result2 = httpx.post(f"{BASE}/step", json={
    "action_type": "query",
    "payload": {
        "sql": """
            SELECT a.name AS artist_name,
                   SUM(CASE WHEN st.skipped_at_sec IS NOT NULL THEN 1 ELSE 0 END) AS skip_count,
                   COUNT(st.id) AS total_streams,
                   ROUND(100.0 * SUM(CASE WHEN st.skipped_at_sec IS NOT NULL THEN 1 ELSE 0 END)
                         / COUNT(st.id), 2) AS skip_rate
            FROM artists a
            JOIN songs s ON a.id = s.artist_id
            JOIN streams st ON s.id = st.song_id
            GROUP BY a.id, a.name
            ORDER BY skip_rate DESC, a.name ASC
        """,
        "question_id": "hard_q4"
    }
}).json()
print(result2["reward"])  # 1.0

# Get final episode score
score = httpx.get(f"{BASE}/grader", params={"task_id": "task_hard"}).json()
print(score["score"])  # 0.0–1.0
```

---

## Setup & Running Locally

```bash
git clone https://github.com/DeveshB-1/meta-pytorch-openenv-hackathon.git
cd meta-pytorch-openenv-hackathon

pip install -r requirements.txt

# Optional: LLM baseline via Groq
echo "GROQ_API_KEY=your_key" > .env

# Start server (port 8000 for local, 7860 for Docker)
uvicorn src.environment.server:app --host 0.0.0.0 --port 8000 --reload

# Open interactive UI
open http://localhost:8000/ui

# Run template baseline (scores 1.0 on all 15 questions)
GROQ_API_KEY="" python scripts/run_baseline.py

# Validate before submission
python scripts/validate.py
```

## Running with Docker

```bash
docker build -t tempo-openenv .
docker run -p 7860:7860 -e GROQ_API_KEY=your_key tempo-openenv
```

---

## Deployment

Auto-deploys to HuggingFace Spaces via GitHub Actions on every push to `main`.

To deploy your own copy:
1. Fork this repo on GitHub
2. Create a HuggingFace Space (Docker SDK, port 7860)
3. Add `HF_TOKEN` and optionally `GROQ_API_KEY` as GitHub Secrets
4. Push to `main` — GitHub Actions handles the rest

---

## What Makes This Environment Interesting for RL

- **Rich behavioural schema** — skip timestamps, completion booleans, and discovery-source labels enable queries that reflect real recommendation-engine analytics
- **Intermediate rewards** — every non-empty result gives `+0.05`, so agents get a gradient signal before finding the exact answer
- **Hint action** — agents can request schema DDL or sample rows at the cost of a step, learning when asking for help is worth it
- **Three difficulty tiers** — easy single-table → medium multi-join → hard window functions/CTEs, each requiring progressively more SQL reasoning
- **MCP endpoint** — plug any MCP-compatible agent in without writing glue code

---

## Differentiators

1. **Domain richness** — music streaming behavioural data (skip rates, source attribution, genre rankings) is far more analytically interesting than generic HR data
2. **Groq LLM Baseline** — Llama 3.3 70B writes SQL from schema alone, no hardcoded answers
3. **Hint mechanism** — RL agent can request schema or sample rows mid-episode
4. **MCP endpoint** — JSON-RPC 2.0 protocol, any MCP-compatible client works out of the box
5. **Interactive UI** — `/ui` lets humans play the environment in a browser
6. **Auto-deploy** — GitHub Actions pushes to HF Spaces on every commit

---

## Author

**Devesh B** — Solo submission for Meta × PyTorch OpenEnv Hackathon x SST 2026

- GitHub: [DeveshB-1](https://github.com/DeveshB-1)
- HuggingFace: [Dev176](https://huggingface.co/Dev176)
- Submission deadline: April 7, 2026

---

## License

MIT
