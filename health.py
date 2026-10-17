
from database import get_connection

FAILURE_THRESHOLD = 3


def init_health():
    with get_connection() as db:
        db.execute("""
            CREATE TABLE IF NOT EXISTS bot_health (
                id INTEGER PRIMARY KEY CHECK (id = 1),
                failures INTEGER NOT NULL DEFAULT 0,
                alerted INTEGER NOT NULL DEFAULT 0
            )
        """)

        db.execute("""
            INSERT OR IGNORE INTO bot_health (
                id, failures, alerted
            )
            VALUES (1, 0, 0)
        """)


def record_failure():
    init_health()

    with get_connection() as db:
        db.execute("""
            UPDATE bot_health
            SET failures = failures + 1
            WHERE id = 1
        """)

        failures, alerted = db.execute("""
            SELECT failures, alerted
            FROM bot_health
            WHERE id = 1
        """).fetchone()

    return failures, bool(alerted)


def mark_alerted():
    with get_connection() as db:
        db.execute("""
            UPDATE bot_health
            SET alerted = 1
            WHERE id = 1
        """)


def get_health():
    init_health()

    with get_connection() as db:
        failures, alerted = db.execute("""
            SELECT failures, alerted
            FROM bot_health
            WHERE id = 1
        """).fetchone()

    return failures, bool(alerted)


def reset_health():
    with get_connection() as db:
        db.execute("""
            UPDATE bot_health
            SET failures = 0, alerted = 0
            WHERE id = 1
        """)
