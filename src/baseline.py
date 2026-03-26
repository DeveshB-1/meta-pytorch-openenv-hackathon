"""
Baseline policy for the SQL Query Environment.

Two modes:
  template — hardcoded correct SQL for all 15 questions (always scores 1.0)
  llm      — Groq LLM writes SQL dynamically given schema + question text

run_baseline_on_env() is called by server.py (/baseline endpoint)
and by scripts/run_baseline.py (HTTP client).
"""
import os
from src.tasks import SCHEMA_DDL, ALL_TASKS

# ---------------------------------------------------------------------------
# Template SQL — correct answers for all 15 questions
# ---------------------------------------------------------------------------

BASELINE_QUERIES: dict[str, str] = {

    # EASY
    "easy_q1": """
        SELECT id, name, department, salary, hire_date, manager_id
        FROM employees
        WHERE department = 'Engineering'
    """,
    "easy_q2": """
        SELECT id, name, department, salary
        FROM employees
        ORDER BY salary DESC
        LIMIT 5
    """,
    "easy_q3": """
        SELECT department, COUNT(*) AS employee_count
        FROM employees
        GROUP BY department
    """,
    "easy_q4": """
        SELECT id, name, department, salary, hire_date
        FROM employees
        WHERE hire_date > '2020-01-01'
    """,
    "easy_q5": """
        SELECT department, ROUND(AVG(salary), 4) AS avg_salary
        FROM employees
        GROUP BY department
    """,

    # MEDIUM
    "medium_q1": """
        SELECT DISTINCT e.name, p.name AS project_name
        FROM employees e
        JOIN assignments a ON e.id = a.employee_id
        JOIN projects p ON a.project_id = p.id
    """,
    "medium_q2": """
        SELECT e.name, SUM(a.hours_worked) AS total_hours
        FROM employees e
        JOIN assignments a ON e.id = a.employee_id
        GROUP BY e.id, e.name
    """,
    "medium_q3": """
        SELECT DISTINCT e.id, e.name, e.department
        FROM employees e
        JOIN assignments a ON e.id = a.employee_id
        JOIN projects p ON a.project_id = p.id
        WHERE p.budget > 100000
    """,
    "medium_q4": """
        SELECT DISTINCT e.department
        FROM employees e
        WHERE e.department NOT IN (
            SELECT DISTINCT e2.department
            FROM employees e2
            JOIN assignments a ON e2.id = a.employee_id
        )
    """,
    "medium_q5": """
        SELECT role, ROUND(AVG(hours_worked), 4) AS avg_hours
        FROM assignments
        GROUP BY role
    """,

    # HARD
    "hard_q1": """
        SELECT name, department, salary,
               RANK() OVER (PARTITION BY department ORDER BY salary DESC) AS salary_rank
        FROM employees
        ORDER BY department, salary_rank
    """,
    "hard_q2": """
        SELECT e.id, e.name, e.department, e.salary
        FROM employees e
        WHERE e.salary > (
            SELECT AVG(salary) FROM employees WHERE department = e.department
        )
    """,
    "hard_q3": """
        SELECT name, budget, start_date,
               SUM(budget) OVER (ORDER BY start_date ROWS UNBOUNDED PRECEDING) AS running_total
        FROM projects
        ORDER BY start_date
    """,
    "hard_q4": """
        SELECT e.name, COUNT(a.project_id) AS project_count
        FROM employees e
        JOIN assignments a ON e.id = a.employee_id
        GROUP BY e.id, e.name
        HAVING COUNT(a.project_id) > 2
    """,
    "hard_q5": """
        SELECT department, name, hire_date
        FROM (
            SELECT department, name, hire_date,
                   RANK() OVER (PARTITION BY department ORDER BY hire_date DESC) AS rk
            FROM employees
        )
        WHERE rk = 1
    """,
}

# ---------------------------------------------------------------------------
# LLM mode — Groq writes SQL dynamically
# ---------------------------------------------------------------------------

SYSTEM_PROMPT = """You are a SQLite SQL expert. Given a database schema and a question, write a single SQL query that answers the question exactly.

Rules:
- Return ONLY the SQL query, no explanation, no markdown, no code fences
- Use exact column aliases as specified in the question
- The database is SQLite (supports window functions)
- Do not add a semicolon at the end
"""


def _ask_groq(question_text: str, columns: list[str]) -> str | None:
    """Ask Groq to write SQL for a question. Returns SQL string or None on failure."""
    try:
        from groq import Groq
        client = Groq(api_key=os.environ["GROQ_API_KEY"])

        user_msg = f"""Schema:
{SCHEMA_DDL}

Question: {question_text}
Expected output columns: {', '.join(columns)}

Write the SQL query:"""

        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user",   "content": user_msg},
            ],
            temperature=0,
            max_tokens=512,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"[baseline] Groq error: {e} — falling back to template")
        return None


# ---------------------------------------------------------------------------
# Run baseline on a live env instance
# ---------------------------------------------------------------------------

def run_baseline_on_env(env, task_id: str, mode: str = "auto") -> list[dict]:
    """
    Step through all questions in a task using baseline SQL.

    mode:
      "auto"     — use LLM if GROQ_API_KEY set, else template
      "template" — always use hardcoded SQL
      "llm"      — always use Groq (raises if key not set)

    Returns list of step results.
    """
    use_llm = (
        mode == "llm"
        or (mode == "auto" and os.environ.get("GROQ_API_KEY"))
    )

    task = ALL_TASKS[task_id]
    results = []

    for question in task.questions:
        sql = None

        if use_llm:
            sql = _ask_groq(question.text, question.columns)

        if sql is None:
            sql = BASELINE_QUERIES[question.id]

        result = env.step({
            "action_type": "query",
            "payload": {
                "sql":         sql,
                "question_id": question.id,
            },
        })
        results.append({
            "question_id": question.id,
            "sql":         sql,
            "reward":      result.reward,
            "rows":        result.observation.get("rows"),
            "error":       result.observation.get("error"),
        })

    return results
