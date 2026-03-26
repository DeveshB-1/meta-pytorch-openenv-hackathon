---
title: OpenEnv SQL Query Environment
emoji: 🗄️
colorFrom: blue
colorTo: green
sdk: docker
app_port: 7860
pinned: false
---

# OpenEnv SQL Query Environment

[![Deploy to HuggingFace Spaces](https://huggingface.co/datasets/huggingface/badges/resolve/main/deploy-to-spaces-sm.svg)](https://huggingface.co/new-space?template=Dev176/openenv-sql-query-env)
[![Live Space](https://img.shields.io/badge/🤗-Live%20Space-blue)](https://huggingface.co/spaces/Dev176/openenv-sql-query-env)
[![GitHub](https://img.shields.io/badge/GitHub-DeveshB--1-black?logo=github)](https://github.com/DeveshB-1/meta-pytorch-openenv-hackathon)

> Built for the **Meta × PyTorch OpenEnv Hackathon x SST 2026** — India's Biggest MEGA AI Hackathon.

An [OpenEnv](https://github.com/huggingface/openenv)-compliant environment where an AI agent writes SQL queries to answer natural language business intelligence questions about an in-memory SQLite database.

**Try it live:** https://huggingface.co/spaces/Dev176/openenv-sql-query-env
**Interactive UI:** https://huggingface.co/spaces/Dev176/openenv-sql-query-env/ui

---

## Environment Description

The agent interacts with a company database (employees, projects, assignments). Each episode presents 5 natural language questions at a chosen difficulty level. The agent submits SQL queries and receives rewards based on correctness — building toward a perfect score of 1.0.

**Database:**
- `employees` — id, name, department, salary, hire_date, manager_id (12 rows)
- `projects` — id, name, budget, start_date, end_date, department (7 rows)
- `assignments` — employee_id, project_id, hours_worked, role (18 rows)

---

## Action & Observation Spaces

### Action Space

**Submit a SQL query:**
```json
{
  "action_type": "query",
  "payload": {
    "sql": "SELECT name FROM employees WHERE department = 'Engineering'",
    "question_id": "easy_q1"
  }
}
```

**Request a hint (costs a step, no reward):**
```json
{ "action_type": "hint", "payload": { "type": "schema" } }
```
```json
{ "action_type": "hint", "payload": { "type": "sample_rows", "table": "employees" } }
```

### Observation Space
```json
{
  "task_id": "task_easy",
  "question_id": "easy_q1",
  "rows": [{"id": 1, "name": "Alice", "department": "Engineering", "salary": 95000.0}],
  "error": null,
  "step": 1,
  "max_steps": 10
}
```

### Reward Structure
| Outcome | Reward |
|---------|--------|
| Correct answer (exact match) | `1.0` |
| Non-empty result (wrong answer) | `0.05` |
| SQL error | `-0.01` |
| Hint | `0.0` |

---

## Tasks

| Task ID | Difficulty | Type | Questions |
|---------|-----------|------|-----------|
| `task_easy` | Easy | Single-table SELECT, WHERE, GROUP BY, LIMIT | 5 |
| `task_medium` | Medium | JOINs, multi-table aggregations | 5 |
| `task_hard` | Hard | Window functions, subqueries, CTEs | 5 |

**Scoring:** average of best-attempt-per-question across all 5 questions in the task.

---

## Setup & Installation

```bash
git clone https://github.com/DeveshB-1/meta-pytorch-openenv-hackathon.git
cd meta-pytorch-openenv-hackathon

pip install -r requirements.txt

# Optional: enable LLM baseline (Groq)
echo "GROQ_API_KEY=your_groq_key" > .env
```

## Running Locally

```bash
# Start server (port 8000)
uvicorn src.environment.server:app --host 0.0.0.0 --port 8000 --reload

# Open interactive UI
open http://localhost:8000/ui

# Run baseline script
python scripts/run_baseline.py
```

## Running with Docker

```bash
docker build -t openenv-sql .
docker run -p 7860:7860 -e GROQ_API_KEY=your_key openenv-sql
```

---

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/reset` | POST | Reset environment, returns schema + questions |
| `/step` | POST | Execute SQL query or hint, returns rows + reward |
| `/state` | GET | Current task, step count, history count |
| `/tasks` | GET | All tasks with questions and action schema |
| `/grader` | GET | Score for current episode (0.0–1.0) |
| `/baseline` | GET | Run LLM/template baseline, return scores for all tasks |
| `/health` | GET | Liveness probe with DB row counts |
| `/mcp` | POST | Model Context Protocol JSON-RPC 2.0 |
| `/ui` | GET | Interactive SQL playground (browser) |

---

## MCP Support

The `/mcp` endpoint implements the [Model Context Protocol](https://modelcontextprotocol.io), allowing any MCP-compatible AI client to auto-discover and use the environment without custom integration code.

```bash
# Discover tools
curl -X POST https://huggingface.co/spaces/Dev176/openenv-sql-query-env/mcp \
  -H "Content-Type: application/json" \
  -d '{"method": "tools/list"}'

# Use a tool
curl -X POST https://huggingface.co/spaces/Dev176/openenv-sql-query-env/mcp \
  -H "Content-Type: application/json" \
  -d '{"method": "tools/call", "params": {"name": "query", "arguments": {"sql": "SELECT * FROM employees LIMIT 3", "question_id": "easy_q1"}}}'
```

Available tools: `reset`, `query`, `hint`

---

## LLM Baseline

When `GROQ_API_KEY` is set, `/baseline` uses **Llama 3.3 70B** (via Groq) to write SQL dynamically given the schema and question — no hardcoded answers. Scores 1.0 on all 3 tasks.

```bash
curl https://huggingface.co/spaces/Dev176/openenv-sql-query-env/baseline
# {"mode": "llm", "scores": {"task_easy": 1.0, "task_medium": 1.0, "task_hard": 1.0}}
```

Falls back to template SQL if no API key is set.

---

## Quick Example

```python
import httpx

BASE = "https://huggingface.co/spaces/Dev176/openenv-sql-query-env"

# Start episode
obs = httpx.post(f"{BASE}/reset", json={"task_id": "task_easy"}).json()
print(obs["observation"]["questions"][0]["text"])
# "List all employees in the Engineering department."

# Submit SQL
result = httpx.post(f"{BASE}/step", json={
    "action_type": "query",
    "payload": {
        "sql": "SELECT * FROM employees WHERE department = 'Engineering'",
        "question_id": "easy_q1"
    }
}).json()
print(result["reward"])  # 1.0

# Get score
score = httpx.get(f"{BASE}/grader", params={"task_id": "task_easy"}).json()
print(score)  # {"task_id": "task_easy", "score": 0.2}
```

---

## Deployment

This repo auto-deploys to HuggingFace Spaces via GitHub Actions on every push to `main`.

To deploy your own copy, click the badge at the top or:
1. Fork this repo
2. Create a HuggingFace Space (Docker SDK)
3. Add `HF_TOKEN` and `GROQ_API_KEY` as GitHub secrets
4. Push to main — GitHub Actions handles the rest

---

## Author

**Devesh B** — Solo submission for Meta × PyTorch OpenEnv Hackathon x SST 2026

- GitHub: [DeveshB-1](https://github.com/DeveshB-1)
- HuggingFace: [Dev176](https://huggingface.co/Dev176)
- Submission deadline: April 7, 2026

---

## License

MIT
