"""
Data layer — database schema, seed data, and 15 questions across 3 tasks.
Expected answers are pre-computed at module load by running reference SQL.
"""
import sqlite3
from dataclasses import dataclass, field


# ---------------------------------------------------------------------------
# Database
# ---------------------------------------------------------------------------

SCHEMA = """
CREATE TABLE employees (
    id          INTEGER PRIMARY KEY,
    name        TEXT    NOT NULL,
    department  TEXT    NOT NULL,
    salary      REAL    NOT NULL,
    hire_date   TEXT    NOT NULL,
    manager_id  INTEGER
);

CREATE TABLE projects (
    id          INTEGER PRIMARY KEY,
    name        TEXT    NOT NULL,
    budget      REAL    NOT NULL,
    start_date  TEXT    NOT NULL,
    end_date    TEXT,
    department  TEXT    NOT NULL
);

CREATE TABLE assignments (
    employee_id  INTEGER NOT NULL,
    project_id   INTEGER NOT NULL,
    hours_worked REAL    NOT NULL,
    role         TEXT    NOT NULL,
    PRIMARY KEY (employee_id, project_id)
);
"""

SEED_EMPLOYEES = [
    (1,  "Alice",   "Engineering", 95000, "2018-03-15", None),
    (2,  "Bob",     "Engineering", 88000, "2019-07-01", 1),
    (3,  "Carol",   "Engineering", 102000,"2017-11-20", 1),
    (4,  "Dave",    "Engineering", 78000, "2021-05-10", 1),
    (5,  "Eve",     "Marketing",   72000, "2020-02-28", None),
    (6,  "Frank",   "Marketing",   68000, "2022-01-15", 5),
    (7,  "Grace",   "Marketing",   75000, "2019-09-03", 5),
    (8,  "Hank",    "HR",          65000, "2020-06-20", None),
    (9,  "Iris",    "HR",          61000, "2021-11-01", 8),
    (10, "Jack",    "HR",          69000, "2018-08-14", 8),
    (11, "Karen",   "Engineering", 91000, "2016-04-05", 1),
    (12, "Leo",     "Marketing",   71000, "2023-03-22", 5),
]

SEED_PROJECTS = [
    (1, "Data Platform",    150000, "2022-01-01", "2023-06-30", "Engineering"),
    (2, "Mobile App",       120000, "2022-03-15", "2023-12-31", "Engineering"),
    (3, "Brand Refresh",     80000, "2022-06-01", "2022-12-31", "Marketing"),
    (4, "CRM Migration",    200000, "2021-09-01", "2023-03-31", "Engineering"),
    (5, "Hiring Pipeline",   50000, "2023-01-01",  None,        "HR"),
    (6, "Ad Campaign Q4",    95000, "2023-07-01", "2023-12-31", "Marketing"),
    (7, "Internal Tools",    60000, "2022-11-01",  None,        "Engineering"),
]

SEED_ASSIGNMENTS = [
    (1,  1, 320, "Lead"),
    (2,  1, 280, "Developer"),
    (3,  2, 350, "Lead"),
    (4,  2, 200, "Developer"),
    (5,  3, 240, "Lead"),
    (6,  3, 180, "Designer"),
    (7,  3, 160, "Analyst"),
    (1,  4, 100, "Architect"),
    (11, 4, 300, "Lead"),
    (2,  4, 220, "Developer"),
    (4,  7, 150, "Developer"),
    (11, 7, 120, "Lead"),
    (8,  5, 200, "Lead"),
    (9,  5, 140, "Coordinator"),
    (5,  6, 190, "Lead"),
    (12, 6, 160, "Designer"),
    (3,  7,  80, "Reviewer"),
    (10, 5,  90, "Analyst"),
]


def create_db() -> sqlite3.Connection:
    """Create a fresh in-memory SQLite DB with seed data."""
    conn = sqlite3.connect(":memory:", check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.executescript(SCHEMA)
    conn.executemany(
        "INSERT INTO employees VALUES (?,?,?,?,?,?)", SEED_EMPLOYEES
    )
    conn.executemany(
        "INSERT INTO projects VALUES (?,?,?,?,?,?)", SEED_PROJECTS
    )
    conn.executemany(
        "INSERT INTO assignments VALUES (?,?,?,?)", SEED_ASSIGNMENTS
    )
    conn.commit()
    return conn


def _rows(conn: sqlite3.Connection, sql: str) -> list[dict]:
    """Run SQL and return results as list of dicts."""
    cur = conn.execute(sql)
    return [dict(row) for row in cur.fetchall()]


# ---------------------------------------------------------------------------
# Question + TaskDef dataclasses
# ---------------------------------------------------------------------------

@dataclass
class Question:
    id: str
    text: str
    expected_rows: list[dict]
    order_sensitive: bool
    columns: list[str]


@dataclass
class TaskDef:
    id: str
    name: str
    difficulty: str
    description: str
    questions: list[Question] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Pre-compute expected answers at module load (reference DB)
# ---------------------------------------------------------------------------

_ref = create_db()

# --- EASY ---

_easy_q1_rows = _rows(_ref, """
    SELECT id, name, department, salary, hire_date, manager_id
    FROM employees
    WHERE department = 'Engineering'
""")

_easy_q2_rows = _rows(_ref, """
    SELECT id, name, department, salary
    FROM employees
    ORDER BY salary DESC
    LIMIT 5
""")

_easy_q3_rows = _rows(_ref, """
    SELECT department, COUNT(*) AS employee_count
    FROM employees
    GROUP BY department
""")

_easy_q4_rows = _rows(_ref, """
    SELECT id, name, department, salary, hire_date
    FROM employees
    WHERE hire_date > '2020-01-01'
""")

_easy_q5_rows = _rows(_ref, """
    SELECT department, ROUND(AVG(salary), 4) AS avg_salary
    FROM employees
    GROUP BY department
""")

# --- MEDIUM ---

_medium_q1_rows = _rows(_ref, """
    SELECT DISTINCT e.name, p.name AS project_name
    FROM employees e
    JOIN assignments a ON e.id = a.employee_id
    JOIN projects p ON a.project_id = p.id
""")

_medium_q2_rows = _rows(_ref, """
    SELECT e.name, SUM(a.hours_worked) AS total_hours
    FROM employees e
    JOIN assignments a ON e.id = a.employee_id
    GROUP BY e.id, e.name
""")

_medium_q3_rows = _rows(_ref, """
    SELECT DISTINCT e.id, e.name, e.department
    FROM employees e
    JOIN assignments a ON e.id = a.employee_id
    JOIN projects p ON a.project_id = p.id
    WHERE p.budget > 100000
""")

_medium_q4_rows = _rows(_ref, """
    SELECT DISTINCT e.department
    FROM employees e
    WHERE e.department NOT IN (
        SELECT DISTINCT e2.department
        FROM employees e2
        JOIN assignments a ON e2.id = a.employee_id
    )
""")

_medium_q5_rows = _rows(_ref, """
    SELECT role, ROUND(AVG(hours_worked), 4) AS avg_hours
    FROM assignments
    GROUP BY role
""")

# --- HARD ---

_hard_q1_rows = _rows(_ref, """
    SELECT name, department, salary,
           RANK() OVER (PARTITION BY department ORDER BY salary DESC) AS salary_rank
    FROM employees
    ORDER BY department, salary_rank
""")

_hard_q2_rows = _rows(_ref, """
    SELECT e.id, e.name, e.department, e.salary
    FROM employees e
    WHERE e.salary > (
        SELECT AVG(salary) FROM employees WHERE department = e.department
    )
""")

_hard_q3_rows = _rows(_ref, """
    SELECT name, budget, start_date,
           SUM(budget) OVER (ORDER BY start_date ROWS UNBOUNDED PRECEDING) AS running_total
    FROM projects
    ORDER BY start_date
""")

_hard_q4_rows = _rows(_ref, """
    SELECT e.name, COUNT(a.project_id) AS project_count
    FROM employees e
    JOIN assignments a ON e.id = a.employee_id
    GROUP BY e.id, e.name
    HAVING COUNT(a.project_id) > 2
""")

_hard_q5_rows = _rows(_ref, """
    SELECT department, name, hire_date
    FROM (
        SELECT department, name, hire_date,
               RANK() OVER (PARTITION BY department ORDER BY hire_date DESC) AS rk
        FROM employees
    )
    WHERE rk = 1
""")

# ---------------------------------------------------------------------------
# Build Task objects
# ---------------------------------------------------------------------------

TASK_EASY = TaskDef(
    id="task_easy",
    name="Easy — Single Table Queries",
    difficulty="easy",
    description="Query a single table using SELECT, WHERE, GROUP BY, ORDER BY, LIMIT.",
    questions=[
        Question("easy_q1", "List all employees in the Engineering department.",
                 _easy_q1_rows, False, ["id", "name", "department", "salary", "hire_date", "manager_id"]),
        Question("easy_q2", "List the top 5 highest paid employees.",
                 _easy_q2_rows, True,  ["id", "name", "department", "salary"]),
        Question("easy_q3", "How many employees are in each department? Return department and employee_count.",
                 _easy_q3_rows, False, ["department", "employee_count"]),
        Question("easy_q4", "List all employees hired after 2020-01-01.",
                 _easy_q4_rows, False, ["id", "name", "department", "salary", "hire_date"]),
        Question("easy_q5", "What is the average salary in each department? Return department and avg_salary.",
                 _easy_q5_rows, False, ["department", "avg_salary"]),
    ],
)

TASK_MEDIUM = TaskDef(
    id="task_medium",
    name="Medium — JOINs and Aggregations",
    difficulty="medium",
    description="Join multiple tables and compute aggregations across them.",
    questions=[
        Question("medium_q1", "List each employee's name and the projects they are assigned to. Return name and project_name.",
                 _medium_q1_rows, False, ["name", "project_name"]),
        Question("medium_q2", "What is the total hours worked per employee? Return name and total_hours.",
                 _medium_q2_rows, False, ["name", "total_hours"]),
        Question("medium_q3", "List distinct employees assigned to projects with budget > 100000. Return id, name, department.",
                 _medium_q3_rows, False, ["id", "name", "department"]),
        Question("medium_q4", "Which departments have no project assignments? Return department.",
                 _medium_q4_rows, False, ["department"]),
        Question("medium_q5", "What is the average hours worked per role? Return role and avg_hours.",
                 _medium_q5_rows, False, ["role", "avg_hours"]),
    ],
)

TASK_HARD = TaskDef(
    id="task_hard",
    name="Hard — Window Functions and Subqueries",
    difficulty="hard",
    description="Use window functions, subqueries, and CTEs to answer complex analytical questions.",
    questions=[
        Question("hard_q1", "Rank employees by salary within their department. Return name, department, salary, salary_rank ordered by department then rank.",
                 _hard_q1_rows, True,  ["name", "department", "salary", "salary_rank"]),
        Question("hard_q2", "List employees who earn above their department's average salary. Return id, name, department, salary.",
                 _hard_q2_rows, False, ["id", "name", "department", "salary"]),
        Question("hard_q3", "Compute the running total of project budgets ordered by start_date. Return name, budget, start_date, running_total.",
                 _hard_q3_rows, True,  ["name", "budget", "start_date", "running_total"]),
        Question("hard_q4", "List employees assigned to more than 2 projects. Return name and project_count.",
                 _hard_q4_rows, False, ["name", "project_count"]),
        Question("hard_q5", "Find the most recently hired employee in each department. Return department, name, hire_date.",
                 _hard_q5_rows, False, ["department", "name", "hire_date"]),
    ],
)

ALL_TASKS: dict[str, TaskDef] = {
    "task_easy":   TASK_EASY,
    "task_medium": TASK_MEDIUM,
    "task_hard":   TASK_HARD,
}

SCHEMA_DDL = """
Table: employees
  id         INTEGER  - unique employee ID
  name       TEXT     - full name
  department TEXT     - Engineering / Marketing / HR
  salary     REAL     - annual salary
  hire_date  TEXT     - YYYY-MM-DD
  manager_id INTEGER  - id of manager (NULL for dept heads)

Table: projects
  id         INTEGER  - unique project ID
  name       TEXT     - project name
  budget     REAL     - total budget
  start_date TEXT     - YYYY-MM-DD
  end_date   TEXT     - YYYY-MM-DD (NULL if ongoing)
  department TEXT     - owning department

Table: assignments
  employee_id  INTEGER  - FK to employees.id
  project_id   INTEGER  - FK to projects.id
  hours_worked REAL     - total hours on this project
  role         TEXT     - Lead / Developer / Designer / Analyst / Coordinator / Reviewer
""".strip()
