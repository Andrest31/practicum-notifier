
import sqlite3
from pathlib import Path

DB_PATH = Path("data/tasks.db")


def get_connection():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)

    connection = sqlite3.connect(DB_PATH)

    connection.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id TEXT PRIMARY KEY,
            discipline TEXT NOT NULL,
            module TEXT NOT NULL,
            type TEXT NOT NULL,
            status TEXT NOT NULL,
            locked INTEGER NOT NULL
        )
    """)

    connection.commit()
    return connection


def check_tasks(tasks):
    """Сохраняет статусы и возвращает задания, которые открылись."""
    opened = []

    with get_connection() as connection:
        for task in tasks:
            previous = connection.execute(
                "SELECT locked FROM tasks WHERE id = ?",
                (task["id"],),
            ).fetchone()

            if previous is not None:
                was_locked = bool(previous[0])

                if was_locked and not task["locked"]:
                    opened.append(task)

            connection.execute(
                """
                INSERT INTO tasks (
                    id, discipline, module, type, status, locked
                )
                VALUES (?, ?, ?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    discipline = excluded.discipline,
                    module = excluded.module,
                    type = excluded.type,
                    status = excluded.status,
                    locked = excluded.locked
                """,
                (
                    task["id"],
                    task["discipline"],
                    task["module"],
                    task["type"],
                    task["status"],
                    int(task["locked"]),
                ),
            )

    return opened
