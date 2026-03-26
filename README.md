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
[![Space](https://img.shields.io/badge/🤗-Live%20Space-blue)](https://huggingface.co/spaces/Dev176/openenv-sql-query-env)

An [OpenEnv](https://github.com/huggingface/openenv)-compliant environment where an AI agent writes SQL queries to answer natural language business intelligence questions about an in-memory SQLite database.

## Environment Description

The agent interacts with a company database containing employees, projects, and assignments. Each episode presents 5 natural language questions. The agent submits SQL queries and receives rewards based on correctness.

**Database schema:**
- `employees` — id, name, department, salary, hire_date, manager_id
- `projects` — id, name, budget, start_date, end_date, department
- `assignments` — employee_id, project_id, hours_worked, role

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
{
  "action_type": "hint",
  "payload": { "type": "schema" }
}
```
```json
{
  "action_type": "hint",
  "payload": { "type": "sample_rows", "table": "employees" }
}
```

### Observation Space
```json
{
  "task_id": "task_easy",
  "question_id": "easy_q1",
  "rows": [{"id": 1, "name": "Alice", "department": "Engineering", "...": "..."}],
  "error": null,
  "step": 1,
  "max_steps": 10
}
```

### Reward
| Outcome | Reward |
|---------|--------|
| Correct answer | `1.0` |
| Non-empty result (wrong answer) | `0.05` |
| SQL error | `-0.01` |
| Hint | `0.0` |

## Tasks

| Task | Difficulty | Description | Score Range |
|------|-----------|-------------|-------------|
| `task_easy` | Easy | Single-table SELECT, WHERE, GROUP BY, LIMIT | 0.0 – 1.0 |
| `task_medium` | Medium | JOINs, multi-table aggregations | 0.0 – 1.0 |
| `task_hard` | Hard | Window functions, subqueries, CTEs | 0.0 – 1.0 |

Each task has 5 questions. Score = average of best-attempt-per-question.

## Setup & Installation

```bash
git clone https://github.com/DeveshB-1/meta-pytorch-openenv-hackathon.git
cd meta-pytorch-openenv-hackathon

pip install -r requirements.txt

# Optional: enable LLM baseline mode
echo "GROQ_API_KEY=your_key_here" > .env
```

## Running the Server

```bash
uvicorn src.environment.server:app --host 0.0.0.0 --port 8000 --reload
```

## Running the Baseline

```bash
python scripts/run_baseline.py
```

## Running with Docker

```bash
docker build -t openenv-sql .
docker run -p 8000:8000 openenv-sql
```

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/reset` | POST | Reset environment, returns schema + questions |
| `/step` | POST | Execute SQL query or hint action |
| `/state` | GET | Current task, step count, history |
| `/tasks` | GET | All tasks with questions and action schema |
| `/grader` | GET | Score for current episode |
| `/baseline` | GET | Run baseline agent, return scores for all tasks |
| `/health` | GET | Liveness probe with DB stats |
| `/mcp` | POST | Model Context Protocol (JSON-RPC 2.0) |

## MCP Support

The `/mcp` endpoint implements the [Model Context Protocol](https://modelcontextprotocol.io), allowing any MCP-compatible AI client to auto-discover and use the environment.

```bash
# List available tools
curl -X POST http://localhost:8000/mcp \
  -H "Content-Type: application/json" \
  -d '{"method": "tools/list"}'

# Use a tool
curl -X POST http://localhost:8000/mcp \
  -H "Content-Type: application/json" \
  -d '{"method": "tools/call", "params": {"name": "query", "arguments": {"sql": "SELECT * FROM employees", "question_id": "easy_q1"}}}'
```

## Evaluation Criteria

- HF Space deploys and responds to `/reset`
- OpenEnv spec compliance (`openenv.yaml`, typed Pydantic models)
- Dockerfile builds and runs
- Baseline script runs without error
- 3 tasks with graders (scores in 0.0–1.0 range)

## License

MIT
