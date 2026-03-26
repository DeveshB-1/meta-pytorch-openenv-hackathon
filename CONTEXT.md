# Session Context — Meta PyTorch OpenEnv Hackathon

Everything you need to pick up and continue from scratch.

---

## Competition

- **Hackathon:** Meta × PyTorch OpenEnv Hackathon x SST (Scaler School of Technology)
- **Dashboard:** https://www.scaler.com/school-of-technology/meta-pytorch-hackathon/dashboard
- **Round 1:** March 25 – April 5, 2026
- **Submission Deadline:** April 7, 2026, 11:59 PM IST
- **Finale (in-person, Bangalore):** April 25–26, 2026
- **Prize pool:** $30,000 | Top teams get Meta/HuggingFace interviews
- **Support:** help_openenvhackathon@scaler.com | Discord community
- **Team:** Devesh B (solo)

---

## What We're Building

**SQL Query Agent Environment** — an OpenEnv-compliant environment where an AI agent must write SQL queries to answer natural language questions about a company database.

### Why this problem?
- Real-world (not a game/toy) — SQL is used daily by analysts, engineers, BI teams
- Objectively gradeable — result rows either match or they don't
- No code sandboxing needed — SQLite runs in-process safely
- Scales cleanly across 3 difficulty levels

### Environment Summary
| | |
|---|---|
| **Action** | `{"action_type": "query", "payload": {"sql": "...", "question_id": "easy_q1"}}` |
| **Observation** | Query result rows, error message, step count, task questions |
| **Reward** | Small per-step signals + final grader score |
| **Max steps** | 10 per episode |
| **Database** | In-memory SQLite: `employees`, `projects`, `assignments` tables |

---

## Repo Structure

```
meta-pytorch-openenv-hackathon/
├── PLAN.md                          ← full implementation plan
├── CONTEXT.md                       ← this file
├── openenv.yaml                     ← OpenEnv spec config (needs updating)
├── Dockerfile                       ← python:3.11-slim, port 8000, uvicorn
├── requirements.txt                 ← fastapi, pydantic, torch, httpx, etc.
├── README.md                        ← has TODOs to fill in
├── src/
│   ├── environment/
│   │   ├── env.py                   ← HackathonEnv abstract base (done) + SQLQueryEnv (TODO)
│   │   └── server.py                ← FastAPI server, all endpoints stubbed (TODO)
│   ├── tasks/
│   │   └── __init__.py              ← EMPTY — needs DB creation + 15 questions
│   ├── graders/
│   │   └── __init__.py              ← EMPTY — needs BaseGrader + row comparison logic
│   └── baseline.py                  ← DOES NOT EXIST YET — template SQL for all 15 questions
├── scripts/
│   ├── run_baseline.py              ← skeleton HTTP client (TODO)
│   └── validate.py                  ← COMPLETE — runs 6 checks against live server
└── tests/
    └── __init__.py
```

---

## Current State

- **Skeleton only** — no environment logic implemented yet
- One commit: "Initial project structure" + PLAN.md added
- GitHub: https://github.com/DeveshB-1/meta-pytorch-openenv-hackathon (make private: `gh repo edit DeveshB-1/meta-pytorch-openenv-hackathon --visibility private`)

---

## What Needs to Be Built (in order)

### 1. `src/tasks/__init__.py` — Data layer (no dependencies)
- `create_db()` → SQLite in-memory with employees/projects/assignments seed data
- `Question` dataclass: `id, text, expected_rows, order_sensitive, columns`
- `TaskDef` dataclass: `id, name, difficulty, description, questions`
- 15 questions total (5 per task), expected answers pre-computed from reference SQL at module load
- Exports: `TASK_EASY`, `TASK_MEDIUM`, `TASK_HARD`, `ALL_TASKS`

**Database schema:**
```sql
employees   (id, name, department, salary, hire_date, manager_id)
projects    (id, name, budget, start_date, end_date, department)
assignments (employee_id, project_id, hours_worked, role)
```
Seed: ~12 employees (Engineering/Marketing/HR), ~7 projects, ~18 assignments — hardcoded/deterministic.

**15 Questions:**

*Easy — single table:*
- easy_q1: All Engineering employees
- easy_q2: Top 5 highest paid employees
- easy_q3: Employee count per department (cols: department, employee_count)
- easy_q4: Employees hired after 2020-01-01
- easy_q5: Average salary by department (cols: department, avg_salary)

*Medium — JOINs:*
- medium_q1: Employee names + their project names (cols: name, project_name)
- medium_q2: Total hours worked per employee (cols: name, total_hours)
- medium_q3: Distinct employees on projects with budget > 100000
- medium_q4: Departments with no project assignments
- medium_q5: Average hours per role (cols: role, avg_hours)

*Hard — window functions / subqueries:*
- hard_q1: Rank employees by salary within dept — ORDER SENSITIVE (cols: name, department, salary, salary_rank)
- hard_q2: Employees earning above their dept average
- hard_q3: Running total of project budgets by start_date — ORDER SENSITIVE (cols: name, budget, start_date, running_total)
- hard_q4: Employees assigned to more than 2 projects (cols: name, project_count)
- hard_q5: Most recent hire per department

### 2. `src/graders/__init__.py` — Grading logic
- `normalize_row(row)` — lowercase keys, round floats to 4dp
- `rows_match(actual, expected, order_sensitive)` → `(bool, reason_str)`
- `SCORE_MAP = {"exact": 1.0, "correct_columns_wrong_values": 0.3, "wrong_structure": 0.0, ...}`
- `BaseGrader.grade(query_history)` → float — best attempt per question, avg across all 5

### 3. `src/graders/task_easy_grader.py`, `task_medium_grader.py`, `task_hard_grader.py`
- Thin subclasses of BaseGrader, each exports a module-level `grader` singleton

### 4. `src/environment/env.py` — Add SQLQueryEnv below existing HackathonEnv
- `reset(task_id="task_easy")` — fresh DB, sets task, clears history
- `step(action)` — execute SQL or hint, track history, intermediate rewards
- `_execute_sql(sql)` → `(rows, error)`
- `get_query_history()`, `get_task()`
- Intermediate rewards: non-empty result → 0.05, SQL error → -0.01, correct → 1.0

### 5. `src/baseline.py` — NEW FILE
- `BASELINE_QUERIES: dict[str, str]` — correct template SQL for all 15 question IDs
- `run_baseline_on_env(env, task_id)` — steps through all questions

### 6. `src/environment/server.py` — Wire everything up
- `env = SQLQueryEnv()` singleton, `GRADERS = {task_id: grader}` dict
- All 6 required endpoints properly implemented
- Also add: `/health`, `/mcp` (MCP protocol)
- `/baseline` uses LLM mode (Claude Haiku via `anthropic` SDK) if `ANTHROPIC_API_KEY` set, else template

### 7. `scripts/run_baseline.py` — HTTP client
- POST /reset → POST /step × N → GET /grader for each task

### 8. `openenv.yaml` + `README.md` — Update descriptions, fix class name to `SQLQueryEnv`

---

## Differentiators (extras that make it stand out)

1. **LLM Baseline** — `/baseline` calls Claude Haiku to write SQL dynamically (falls back to templates without API key)
2. **Hint Action** — `{"action_type": "hint", "payload": {"type": "schema"}}` returns DDL; `{"type": "sample_rows", "table": "employees"}` returns 3 rows
3. **`/mcp` endpoint** — MCP JSON-RPC 2.0 protocol (`tools/list`, `tools/call`) — mentioned in OpenEnv spec
4. **`/health` endpoint** — returns DB stats, useful for HF Spaces liveness probes
5. **Intermediate rewards** — per-step reward signals make env more RL-friendly

---

## Key Gotchas

- Use `pydantic` v2 `.model_dump()` not `.dict()`
- SQLite window functions need SQLite 3.25+ — python:3.11-slim ships 3.39 ✓
- `sqlite3.connect(":memory:", check_same_thread=False)` for thread safety
- `/baseline` mutates global env — reset after, or use local instance
- `/grader` must check that current task matches requested task_id
- Column names in SQL aliases must match exactly what the grader expects
- Pre-compute expected answers at module load time using `_ref_con`

---

## Verification Steps

```bash
# Install deps
pip install -r requirements.txt

# Start server
uvicorn src.environment.server:app --host 0.0.0.0 --port 8000

# Run validation (all 6 checks)
python scripts/validate.py

# Run baseline
python scripts/run_baseline.py

# Docker
docker build -t openenv-hackathon .
docker run -p 8000:8000 openenv-hackathon
```

---

## Environment Variables

```bash
ANTHROPIC_API_KEY=sk-...   # optional — enables LLM baseline mode
```

Create a `.env` file (already in `.gitignore`).

---

## Deployment (after building)

1. Create HuggingFace Space (Docker type)
2. Push repo to HF Space
3. Set `ANTHROPIC_API_KEY` as HF Space secret
4. Submit Space URL to Scaler dashboard
