# Meta PyTorch OpenEnv Hackathon — Implementation Plan

## Context
Building a complete OpenEnv-compliant submission for the Meta × PyTorch OpenEnv Hackathon 2026 (Round 1: March 25 – April 5, deadline April 7). The repo has a skeleton in place (FastAPI server, Dockerfile, openenv.yaml, abstract base class) but **nothing is implemented** — all endpoints return stubs and no environment logic exists.

**Chosen problem domain: SQL Query Agent Environment**
An AI agent interacts with an in-memory SQLite database (employees / projects / assignments) and must write SQL queries to answer natural language questions. Real-world, objectively gradeable, no sandboxing needed.

---

## Hackathon Requirements (from Scaler dashboard)
- Round 1: March 25 – April 5 | **Deadline: April 7, 2026 11:59 PM**
- Must expose: `/reset`, `/step`, `/state`, `/tasks`, `/grader`, `/baseline`
- Min 3 tasks with graded difficulty, scores 0.0–1.0
- Dockerized + deployed to HuggingFace Spaces
- `openenv.yaml` must be valid and reference correct class names
- Support email: help_openenvhackathon@scaler.com

---

## Environment Design

### SQLQueryEnv
| | |
|---|---|
| **State** | In-memory SQLite DB + current task + query history |
| **Action** | `{"action_type": "query", "payload": {"sql": "SELECT ...", "question_id": "easy_q1"}}` |
| **Observation** | `{"task_id", "questions", "rows", "error", "step", "schema" (on reset)}` |
| **Reward** | 0.0 per step; final score from `/grader` after episode |
| **Max steps** | 10 per episode |

### Database Schema
```sql
employees   (id, name, department, salary, hire_date, manager_id)
projects    (id, name, budget, start_date, end_date, department)
assignments (employee_id, project_id, hours_worked, role)
```
Seed data: ~12 employees (3 depts), ~7 projects, ~18 assignments — deterministic/hardcoded.

### 3 Tasks (5 questions each)

**task_easy** — Single-table SELECT:
- Q1: All Engineering employees
- Q2: Top 5 highest paid employees
- Q3: Employee count per department
- Q4: Employees hired after 2020-01-01
- Q5: Average salary by department

**task_medium** — JOINs & aggregations:
- Q1: Employees and their project names
- Q2: Total hours worked per employee
- Q3: Employees on projects with budget > 100000
- Q4: Departments with no assignments
- Q5: Average hours worked per role

**task_hard** — Window functions & subqueries:
- Q1: Rank employees by salary within department *(order-sensitive)*
- Q2: Employees earning above their dept average
- Q3: Running total of project budgets by start_date *(order-sensitive)*
- Q4: Employees assigned to more than 2 projects
- Q5: Most recent hire per department

### Grading Logic
- Score = avg of best-attempt-per-question across all 5 questions
- Exact match → 1.0 | Correct columns, wrong values → 0.3 | Wrong structure → 0.0
- Order-insensitive comparison (sort rows) except Q1/Q3 of hard task
- Float values normalized to 4 decimal places

---

## Files to Create / Modify

### 1. `src/tasks/__init__.py` ← most critical, no deps
- `create_db() -> sqlite3.Connection` — creates in-memory DB with seed data
- `Question` dataclass: `id, text, expected_rows, order_sensitive, columns`
- `TaskDef` dataclass: `id, name, difficulty, description, questions`
- 15 `Question` instances with expected answers pre-computed at module load via reference SQL
- `TASK_EASY`, `TASK_MEDIUM`, `TASK_HARD`, `ALL_TASKS: dict[str, TaskDef]`

### 2. `src/graders/__init__.py`
- `normalize_row(row)` — lowercases keys, rounds floats to 4dp
- `rows_match(actual, expected, order_sensitive) -> (bool, str)` — returns reason string
- `SCORE_MAP: dict[str, float]` — maps reason → partial credit score
- `BaseGrader` with `grade(query_history) -> float` — best-attempt-per-question

### 3. `src/graders/task_easy_grader.py`, `task_medium_grader.py`, `task_hard_grader.py`
- Each: thin subclass of `BaseGrader`, imports its `TaskDef`, exposes module-level `grader` singleton

### 4. `src/environment/env.py`
- Keep existing `HackathonEnv` abstract class and `StepResult`
- Add `SQLQueryEnv(HackathonEnv)`:
  - `reset(task_id="task_easy") -> dict` — creates fresh DB, sets task, clears history
  - `step(action) -> StepResult` — executes SQL, records in history, increments step
  - `state() -> dict` — sanitized state (no connection object)
  - `get_query_history() -> list[dict]`
  - `get_task() -> TaskDef | None`
  - `_execute_sql(sql) -> (rows, error)` — wraps sqlite3.Error

### 5. `src/environment/server.py`
- Module-level: `env = SQLQueryEnv()`, `GRADERS = {task_id: grader_instance}`
- `/reset` (POST): accepts `{"task_id": "task_easy"}`, returns initial observation
- `/step` (POST): delegates to `env.step()`, returns `result.model_dump()`
- `/state` (GET): delegates to `env.state()`
- `/tasks` (GET): returns full task metadata from `ALL_TASKS`
- `/grader` (GET): calls `GRADERS[task_id].grade(env.get_query_history())`, checks task_id mismatch
- `/baseline` (GET): loops over all tasks — reset, submit template SQL, grade, return all scores

### 6. `src/baseline.py` *(new)*
- `BASELINE_QUERIES: dict[str, str]` — maps question_id → correct template SQL (all 15)
- `run_baseline_on_env(env, task_id)` — steps through all questions with template SQL
- Shared by `server.py` (in-process) and `scripts/run_baseline.py` (HTTP client)

### 7. `scripts/run_baseline.py`
- Implement `run_episode(task_id)`: POST /reset → POST /step × N → GET /grader
- Uses `BASELINE_QUERIES` from `src/baseline.py`

### 8. `openenv.yaml`
- Update `description`, `environment.class: SQLQueryEnv`, task descriptions

### 9. `README.md`
- Fill all TODO sections with actual env description, action/observation space docs

---

## Implementation Order
1. `src/tasks/__init__.py`
2. `src/graders/__init__.py`
3. `src/graders/task_easy_grader.py`, `task_medium_grader.py`, `task_hard_grader.py`
4. `src/environment/env.py` (add SQLQueryEnv)
5. `src/baseline.py`
6. `src/environment/server.py`
7. `scripts/run_baseline.py`
8. `openenv.yaml` + `README.md`

---

## Interesting Extras (differentiators)

### 1. LLM-Powered Baseline (Claude API)
Instead of hardcoded template SQL, `/baseline` actually calls **Claude claude-haiku-4-5-20251001** to write SQL dynamically given the schema + question. Far more impressive and directly relevant to the AI/PyTorch theme.
- Add `anthropic` to `requirements.txt`
- `src/baseline.py` has two modes: `template` (fast, deterministic) and `llm` (Claude writes the SQL)
- `/baseline` uses LLM mode; `ANTHROPIC_API_KEY` from env var (`.env` file, loaded via `python-dotenv`)
- System prompt: "You are a SQL expert. Given a SQLite schema and a question, write a single SQL query."
- Falls back to template mode if API key not set

### 2. Hint Action Type
Agent can spend a step to request schema help instead of submitting SQL:
- `{"action_type": "hint", "payload": {"type": "sample_rows", "table": "employees"}}` → returns 3 sample rows
- `{"action_type": "hint", "payload": {"type": "schema"}}` → returns full DDL + column descriptions
- Hints cost a step but return no reward — helps LLM agents that need to explore the schema

### 3. `/mcp` Endpoint (MCP Protocol)
OpenEnv spec explicitly supports MCP (Model Context Protocol / JSON-RPC 2.0). Adding this makes the submission fully spec-compliant and more impressive to judges.
- `POST /mcp` with `{"method": "tools/list"}` → returns available tools
- `POST /mcp` with `{"method": "tools/call", "params": {"name": "query", "arguments": {...}}}` → wraps `step()`
- Exposes: `query`, `reset`, `hint` as MCP tools

### 4. `/health` Endpoint
Quick health check useful for HF Spaces liveness probes:
- Returns `{"status": "ok", "db_stats": {"employees": N, "projects": N, "assignments": N}}`
- Validates DB is live and seeded correctly

### 5. Intermediate Step Rewards
Instead of all reward at episode end, give small per-step signal:
- Query returns non-empty result → `reward = 0.05` (agent is making progress)
- Query returns SQL error → `reward = -0.01` (discourages garbage SQL)
- Correct answer → `reward = 1.0` (checked inline during step)
- This makes the environment more RL-friendly and impressive to judges

---

## Key Gotchas
- **Pydantic v2**: use `.model_dump()` not `.dict()`
- **SQLite window functions**: supported in SQLite 3.25+ (python:3.11-slim ships 3.39+) ✓
- **Thread safety**: use `check_same_thread=False` on sqlite3 connection
- **`/baseline` mutates global env**: document this; call `env.reset()` after baseline run
- **`/grader` task mismatch**: check `env.get_task().id == task_id` and return warning if not
- **Column aliases matter**: question text must specify exact expected column names
- **Pre-compute expected answers**: run reference SQL at module load time against `_ref_con`

---

## Pending Actions (after plan mode)
- Copy this plan into repo as `PLAN.md` so it's tracked in git and pushed to GitHub
- Make GitHub repo **private**: `gh repo edit DeveshB-1/meta-pytorch-openenv-hackathon --visibility private`

---

## Verification
1. `uvicorn src.environment.server:app --host 0.0.0.0 --port 8000`
2. `python scripts/validate.py` — all 6 checks must pass ✓
3. `python scripts/run_baseline.py` — should print scores (1.0/1.0/1.0 for template baseline)
4. `docker build -t openenv-hackathon . && docker run -p 8000:8000 openenv-hackathon`
5. Hit `/baseline` → should return scores for all 3 tasks
