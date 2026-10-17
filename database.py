
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

    connection.execute("""
        CREATE TABLE IF NOT EXISTS notifications (
            task_id TEXT PRIMARY KEY,
            message TEXT NOT NULL,
            sent INTEGER NOT NULL DEFAULT 0
        )
    """)

    connection.commit()
    return connection


def check_tasks(tasks):
    """Обновляет задания и ставит новые открытия в очередь."""
    opened = []

    with get_connection() as connection:
        for task in tasks:
            previous = connection.execute(
                "SELECT locked FROM tasks WHERE id = ?",
                (task["id"],),
            ).fetchone()

            if previous is not None and previous[0] and not task["locked"]:
                opened.append(task)

                message = (
                    f"🟢 {task['discipline']}\n"
                    f"{task['module']}\n"
                    f"{task['type']} — открылся!"
                )

                connection.execute(
                    """
                    INSERT OR IGNORE INTO notifications (task_id, message)
                    VALUES (?, ?)
                    """,
                    (task["id"], message),
                )

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


def get_pending_notifications():
    with get_connection() as connection:
        return connection.execute(
            "SELECT task_id, message FROM notifications WHERE sent = 0"
        ).fetchall()


def mark_notification_sent(task_id):
    with get_connection() as connection:
        connection.execute(
            "UPDATE notifications SET sent = 1 WHERE task_id = ?",
            (task_id,),
        )
