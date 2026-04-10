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
        SELECT id, title, genre, bpm, mood, duration_sec, release_year
        FROM songs
        WHERE genre = 'Electronic'
    """,
    "easy_q2": """
        SELECT id, name, country, monthly_listeners
        FROM artists
        ORDER BY monthly_listeners DESC, name ASC
        LIMIT 5
    """,
    "easy_q3": """
        SELECT genre, COUNT(*) AS song_count
        FROM songs
        GROUP BY genre
        ORDER BY song_count DESC, genre ASC
    """,
    "easy_q4": """
        SELECT id, username, country, subscription_tier
        FROM users
        WHERE subscription_tier = 'premium'
    """,
    "easy_q5": """
        SELECT subscription_tier, COUNT(*) AS user_count
        FROM users
        GROUP BY subscription_tier
    """,

    # MEDIUM
    "medium_q1": """
        SELECT s.title, COUNT(st.id) AS stream_count
        FROM songs s
        JOIN streams st ON s.id = st.song_id
        GROUP BY s.id, s.title
        ORDER BY stream_count DESC, s.title ASC
        LIMIT 10
    """,
    "medium_q2": """
        SELECT a.name AS artist_name,
               ROUND(100.0 * SUM(st.completed) / COUNT(st.id), 2) AS completion_rate
        FROM artists a
        JOIN songs s ON a.id = s.artist_id
        JOIN streams st ON s.id = st.song_id
        GROUP BY a.id, a.name
        ORDER BY completion_rate DESC, a.name ASC
    """,
    "medium_q3": """
        SELECT source, COUNT(*) AS stream_count
        FROM streams
        GROUP BY source
        ORDER BY stream_count DESC, source ASC
    """,
    "medium_q4": """
        SELECT u.username, COUNT(DISTINCT st.song_id) AS unique_songs
        FROM users u
        JOIN streams st ON u.id = st.user_id
        GROUP BY u.id, u.username
        ORDER BY unique_songs DESC, u.username ASC
        LIMIT 10
    """,
    "medium_q5": """
        SELECT s.mood, COUNT(st.id) AS stream_count
        FROM songs s
        JOIN streams st ON s.id = st.song_id
        WHERE st.completed = 1
        GROUP BY s.mood
        ORDER BY stream_count DESC, s.mood ASC
    """,

    # ANALYTICS
    "analytics_q1": """
        SELECT s.genre,
               SUM(CASE WHEN u.subscription_tier = 'premium' THEN 2 ELSE 1 END) AS revenue_proxy,
               COUNT(st.id) AS total_streams,
               ROUND(100.0 * SUM(CASE WHEN u.subscription_tier = 'premium' THEN 1 ELSE 0 END) / COUNT(st.id), 2) AS premium_stream_pct
        FROM streams st
        JOIN songs s ON st.song_id = s.id
        JOIN users u ON st.user_id = u.id
        GROUP BY s.genre
        ORDER BY revenue_proxy DESC, s.genre ASC
    """,
    "analytics_q2": """
        SELECT a.name AS artist_name,
               COUNT(st.id) AS total_streams,
               SUM(st.completed) AS completed_streams,
               ROUND(100.0 * SUM(st.completed) / COUNT(st.id), 2) AS engagement_rate
        FROM artists a
        JOIN songs s ON a.id = s.artist_id
        JOIN streams st ON s.id = st.song_id
        GROUP BY a.id, a.name
        HAVING COUNT(st.id) >= 5
        ORDER BY engagement_rate DESC, a.name ASC
    """,
    "analytics_q3": """
        SELECT s.genre, u.subscription_tier, COUNT(st.id) AS stream_count
        FROM streams st
        JOIN songs s ON st.song_id = s.id
        JOIN users u ON st.user_id = u.id
        GROUP BY s.genre, u.subscription_tier
        ORDER BY s.genre ASC, u.subscription_tier ASC
    """,
    "analytics_q4": """
        SELECT a.name AS artist_name,
               COUNT(st.id) AS total_streams,
               COUNT(DISTINCT st.user_id) AS unique_listeners,
               ROUND(100.0 * SUM(st.completed) / COUNT(st.id), 2) AS completion_rate
        FROM artists a
        JOIN songs s ON a.id = s.artist_id
        JOIN streams st ON s.id = st.song_id
        GROUP BY a.id, a.name
        ORDER BY total_streams DESC, a.name ASC
        LIMIT 10
    """,
    "analytics_q5": """
        WITH y2024 AS (
            SELECT user_id, COUNT(*) AS streams_2024 FROM streams
            WHERE played_at >= '2024-01-01' AND played_at < '2025-01-01'
            GROUP BY user_id
        ),
        y2025 AS (
            SELECT user_id, COUNT(*) AS streams_2025 FROM streams
            WHERE played_at >= '2025-01-01' AND played_at < '2026-01-01'
            GROUP BY user_id
        )
        SELECT u.username, u.subscription_tier, y24.streams_2024, y25.streams_2025
        FROM users u
        JOIN y2024 y24 ON u.id = y24.user_id
        JOIN y2025 y25 ON u.id = y25.user_id
        ORDER BY y24.streams_2024 + y25.streams_2025 DESC, u.username ASC
    """,

    # REALTIME
    "realtime_q1": """
        SELECT SUBSTR(played_at, 1, 7) AS year_month, COUNT(*) AS stream_count
        FROM streams
        GROUP BY year_month
        ORDER BY year_month ASC
    """,
    "realtime_q2": """
        SELECT s.title, a.name AS artist_name, COUNT(st.id) AS streams_2025
        FROM songs s
        JOIN artists a ON s.artist_id = a.id
        LEFT JOIN streams st ON s.id = st.song_id AND SUBSTR(st.played_at, 1, 4) = '2025'
        WHERE s.release_year = 2025
        GROUP BY s.id, s.title, a.name
        ORDER BY streams_2025 DESC, s.title ASC
    """,
    "realtime_q3": """
        SELECT s.title, a.name AS artist_name, COUNT(st.id) AS recommendation_streams
        FROM streams st
        JOIN songs s ON st.song_id = s.id
        JOIN artists a ON s.artist_id = a.id
        WHERE st.source = 'recommendation' AND SUBSTR(st.played_at, 1, 4) = '2024'
        GROUP BY s.id, s.title, a.name
        ORDER BY recommendation_streams DESC, s.title ASC
        LIMIT 10
    """,
    "realtime_q4": """
        WITH jan AS (
            SELECT s.genre, COUNT(*) AS jan_streams FROM streams st
            JOIN songs s ON st.song_id = s.id
            WHERE SUBSTR(st.played_at, 1, 7) = '2024-01' GROUP BY s.genre
        ),
        feb AS (
            SELECT s.genre, COUNT(*) AS feb_streams FROM streams st
            JOIN songs s ON st.song_id = s.id
            WHERE SUBSTR(st.played_at, 1, 7) = '2024-02' GROUP BY s.genre
        )
        SELECT j.genre, j.jan_streams, COALESCE(f.feb_streams, 0) AS feb_streams,
               ROUND(100.0 * (COALESCE(f.feb_streams, 0) - j.jan_streams) / j.jan_streams, 2) AS mom_growth_pct
        FROM jan j LEFT JOIN feb f ON j.genre = f.genre
        ORDER BY mom_growth_pct DESC, j.genre ASC
    """,
    "realtime_q5": """
        SELECT SUBSTR(played_at, 1, 7) AS year_month,
               COUNT(*) AS total_streams,
               SUM(CASE WHEN skipped_at_sec IS NOT NULL THEN 1 ELSE 0 END) AS skipped_streams,
               ROUND(100.0 * SUM(CASE WHEN skipped_at_sec IS NOT NULL THEN 1 ELSE 0 END) / COUNT(*), 2) AS skip_rate_pct
        FROM streams
        GROUP BY year_month
        ORDER BY year_month ASC
    """,

    # HARD
    "hard_q1": """
        SELECT s.title, COUNT(st.id) AS stream_count,
               RANK() OVER (PARTITION BY s.genre ORDER BY COUNT(st.id) DESC) AS genre_rank
        FROM songs s
        JOIN streams st ON s.id = st.song_id
        GROUP BY s.id, s.title, s.genre
        ORDER BY s.genre ASC, genre_rank ASC, s.title ASC
    """,
    "hard_q2": """
        SELECT u.username, u.country,
               COUNT(st.id) AS total_streams,
               ROUND(100.0 * SUM(st.completed) / COUNT(st.id), 2) AS completion_rate
        FROM users u
        JOIN streams st ON u.id = st.user_id
        WHERE u.subscription_tier = 'free'
        GROUP BY u.id, u.username, u.country
        HAVING COUNT(st.id) > 5
    """,
    "hard_q3": """
        WITH song_streams AS (
            SELECT song_id, COUNT(*) AS stream_count
            FROM streams
            GROUP BY song_id
        ),
        avg_streams AS (
            SELECT AVG(stream_count) AS avg_count FROM song_streams
        )
        SELECT s.title, s.genre, ss.stream_count
        FROM songs s
        JOIN song_streams ss ON s.id = ss.song_id
        WHERE ss.stream_count > (SELECT avg_count FROM avg_streams)
        ORDER BY ss.stream_count DESC, s.title ASC
    """,
    "hard_q4": """
        SELECT a.name AS artist_name,
               SUM(CASE WHEN st.skipped_at_sec IS NOT NULL THEN 1 ELSE 0 END) AS skip_count,
               COUNT(st.id) AS total_streams,
               ROUND(100.0 * SUM(CASE WHEN st.skipped_at_sec IS NOT NULL THEN 1 ELSE 0 END) / COUNT(st.id), 2) AS skip_rate
        FROM artists a
        JOIN songs s ON a.id = s.artist_id
        JOIN streams st ON s.id = st.song_id
        GROUP BY a.id, a.name
        ORDER BY skip_rate DESC, a.name ASC
    """,
    "hard_q5": """
        SELECT p.name AS playlist_name, u.username, COUNT(ps.song_id) AS song_count
        FROM playlists p
        JOIN users u ON p.user_id = u.id
        JOIN playlist_songs ps ON p.id = ps.playlist_id
        GROUP BY p.id, p.name, u.username
        ORDER BY song_count DESC, p.name ASC
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


def _ask_llm(question_text: str, columns: list[str]) -> str | None:
    """Ask LLM to write SQL using OpenAI client + API_BASE_URL/MODEL_NAME env vars."""
    api_key  = os.environ.get("OPENAI_API_KEY") or os.environ.get("API_KEY") or os.environ.get("GROQ_API_KEY")
    api_base = os.environ.get("API_BASE_URL", "https://api.groq.com/openai/v1")
    model    = os.environ.get("MODEL_NAME", "llama-3.3-70b-versatile")

    if not api_key:
        return None

    try:
        from openai import OpenAI
        client = OpenAI(api_key=api_key, base_url=api_base)

        user_msg = (
            f"Schema:\n{SCHEMA_DDL}\n\n"
            f"Question: {question_text}\n"
            f"Expected output columns: {', '.join(columns)}\n\n"
            f"Write the SQL query:"
        )

        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user",   "content": user_msg},
            ],
            temperature=0,
            max_tokens=512,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"[baseline] LLM error: {e} — falling back to template")
        return None


# ---------------------------------------------------------------------------
# Run baseline on a live env instance
# ---------------------------------------------------------------------------

def run_baseline_on_env(env, task_id: str, mode: str = "auto") -> list[dict]:
    """
    Step through all questions in a task using baseline SQL.

    mode:
      "auto"     — use LLM if OPENAI_API_KEY or API_KEY set, else template
      "template" — always use hardcoded SQL
      "llm"      — always use LLM (raises if key not set)

    Returns list of step results.
    """
    use_llm = (
        mode == "llm"
        or (mode == "auto" and (os.environ.get("OPENAI_API_KEY") or os.environ.get("API_KEY") or os.environ.get("GROQ_API_KEY")))
    )

    task = ALL_TASKS[task_id]
    results = []

    for question in task.questions:
        sql = None

        if use_llm:
            sql = _ask_llm(question.text, question.columns)

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
