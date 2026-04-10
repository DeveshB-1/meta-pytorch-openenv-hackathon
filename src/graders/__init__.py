"""
Grading logic — compares agent SQL results to expected answers and returns 0.0–1.0 scores.

Scoring tiers:
  0.95 — exact match (correct columns + all rows match)
  0.80 — partial match, ≥ 80 % of expected rows present
  0.60 — partial match, ≥ 50 % of expected rows present
  0.40 — correct columns, < 50 % rows match
  0.05 — wrong column structure or SQL error
"""
from src.tasks import TaskDef


# ---------------------------------------------------------------------------
# Score tiers
# ---------------------------------------------------------------------------

SCORE_MAP = {
    "exact":                       0.95,
    "correct_columns_wrong_values": 0.4,
    "wrong_structure":              0.05,
    "sql_error":                    0.05,
    "no_attempt":                   0.05,
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
        if not norm_actual:
            return True, "exact"
        return False, "wrong_structure"

    expected_cols = set(norm_expected[0].keys())

    if not norm_actual:
        return False, "wrong_structure"

    actual_cols = set(norm_actual[0].keys())

    if actual_cols != expected_cols:
        return False, "wrong_structure"

    # Columns match — now compare values
    if not order_sensitive:
        norm_actual   = sorted(norm_actual,   key=lambda r: str(sorted(r.items())))
        norm_expected = sorted(norm_expected, key=lambda r: str(sorted(r.items())))

    if norm_actual == norm_expected:
        return True, "exact"

    return False, "correct_columns_wrong_values"


def _partial_overlap(actual: list[dict], expected: list[dict], order_sensitive: bool) -> float:
    """
    Fraction of expected rows that appear in the actual result (0.0–1.0).

    Used to give partial credit when columns are right but values differ.
    Order-insensitive: checks set membership.
    Order-sensitive: checks positional alignment.
    """
    norm_actual   = [normalize_row(r) for r in actual]
    norm_expected = [normalize_row(r) for r in expected]

    if not norm_expected:
        return 1.0

    if order_sensitive:
        matches = sum(a == e for a, e in zip(norm_actual, norm_expected))
    else:
        actual_strs = {str(sorted(r.items())) for r in norm_actual}
        matches = sum(
            1 for r in norm_expected if str(sorted(r.items())) in actual_strs
        )

    return matches / len(norm_expected)


# ---------------------------------------------------------------------------
# Base grader
# ---------------------------------------------------------------------------

class BaseGrader:
    def __init__(self, task: TaskDef):
        self.task = task

    def grade(self, query_history: list[dict]) -> float:
        """
        Score a completed episode with partial-row credit.

        query_history is a list of dicts from env.step():
          {"question_id": "easy_q1", "rows": [...], "error": str | None}

        Returns float strictly in (0, 1).
        """
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
                    matched, reason = rows_match(rows, question.expected_rows, question.order_sensitive)
                    if matched:
                        score = SCORE_MAP["exact"]  # 0.95
                    elif reason == "correct_columns_wrong_values":
                        overlap = _partial_overlap(rows, question.expected_rows, question.order_sensitive)
                        if overlap >= 0.8:
                            score = 0.80
                        elif overlap >= 0.5:
                            score = 0.60
                        else:
                            score = 0.40
                    else:
                        score = SCORE_MAP[reason]  # wrong_structure or sql_error → 0.05

                if score > best:
                    best = score

            total_score += best

        raw = round(total_score / len(self.task.questions), 4)
        # Validator requires strictly (0, 1) — clamp away from boundaries
        return max(0.0001, min(0.9999, raw))
