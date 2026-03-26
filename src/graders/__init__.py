"""
Grading logic — compares agent SQL results to expected answers and returns 0.0–1.0 scores.
"""
from src.tasks import TaskDef


# ---------------------------------------------------------------------------
# Score tiers
# ---------------------------------------------------------------------------

SCORE_MAP = {
    "exact":                       1.0,
    "correct_columns_wrong_values": 0.3,
    "wrong_structure":              0.0,
    "sql_error":                    0.0,
    "no_attempt":                   0.0,
}


# ---------------------------------------------------------------------------
# Row normalization
# ---------------------------------------------------------------------------

def normalize_row(row: dict) -> dict:
    """Lowercase all keys and round floats to 4 decimal places."""
    out = {}
    for k, v in row.items():
        key = k.lower()
        if isinstance(v, float):
            out[key] = round(v, 4)
        else:
            out[key] = v
    return out


# ---------------------------------------------------------------------------
# Row comparison
# ---------------------------------------------------------------------------

def rows_match(actual: list[dict], expected: list[dict], order_sensitive: bool) -> tuple[bool, str]:
    """
    Compare actual rows to expected rows.
    Returns (matched: bool, reason: str).

    reason is one of:
      "exact"                        — rows match perfectly
      "correct_columns_wrong_values" — same column names, different data
      "wrong_structure"              — column names don't match
      "sql_error"                    — actual is None (query failed)
    """
    if actual is None:
        return False, "sql_error"

    norm_actual   = [normalize_row(r) for r in actual]
    norm_expected = [normalize_row(r) for r in expected]

    # Check column structure using first expected row
    if not norm_expected:
        # Expected empty result — check if actual is also empty
        if not norm_actual:
            return True, "exact"
        return False, "wrong_structure"

    expected_cols = set(norm_expected[0].keys())

    if not norm_actual:
        # Agent returned nothing but we expected something
        # If columns can't be checked, call it wrong structure
        return False, "wrong_structure"

    actual_cols = set(norm_actual[0].keys())

    if actual_cols != expected_cols:
        return False, "wrong_structure"

    # Columns match — now compare values
    if not order_sensitive:
        # Sort rows by their string representation for order-insensitive comparison
        norm_actual   = sorted(norm_actual,   key=lambda r: str(sorted(r.items())))
        norm_expected = sorted(norm_expected, key=lambda r: str(sorted(r.items())))

    if norm_actual == norm_expected:
        return True, "exact"

    return False, "correct_columns_wrong_values"


# ---------------------------------------------------------------------------
# Base grader
# ---------------------------------------------------------------------------

class BaseGrader:
    def __init__(self, task: TaskDef):
        self.task = task

    def grade(self, query_history: list[dict]) -> float:
        """
        Score a completed episode.

        query_history is a list of dicts, each entry from env.step():
          {
            "question_id": "easy_q1",
            "rows": [...],   # None if SQL error
            "error": str | None
          }

        Returns float in [0.0, 1.0].
        """
        # Build a map: question_id → list of (rows, error) attempts
        attempts: dict[str, list] = {q.id: [] for q in self.task.questions}

        for entry in query_history:
            qid = entry.get("question_id")
            if qid in attempts:
                attempts[qid].append({
                    "rows":  entry.get("rows"),
                    "error": entry.get("error"),
                })

        total_score = 0.0

        for question in self.task.questions:
            qid = question.id
            best = 0.0

            for attempt in attempts[qid]:
                rows  = attempt["rows"]
                error = attempt["error"]

                if error or rows is None:
                    score = SCORE_MAP["sql_error"]
                else:
                    _, reason = rows_match(rows, question.expected_rows, question.order_sensitive)
                    score = SCORE_MAP[reason]

                if score > best:
                    best = score

                if best == 1.0:
                    break  # can't do better

            total_score += best

        return round(total_score / len(self.task.questions), 4)
