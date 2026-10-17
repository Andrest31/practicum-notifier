
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
            locked INTEGER NOT NULL,
            url TEXT
        )
    """)

    connection.execute("""
        CREATE TABLE IF NOT EXISTS notifications (
            task_id TEXT PRIMARY KEY,
            message TEXT NOT NULL,
            sent INTEGER NOT NULL DEFAULT 0
        )
    """)

    # Миграция старой базы без потери данных
    columns = {
        row[1]
        for row in connection.execute("PRAGMA table_info(tasks)")
    }

    if "url" not in columns:
        connection.execute(
            "ALTER TABLE tasks ADD COLUMN url TEXT"
        )

    connection.commit()
    return connection



def format_notification(task):
    """Формирует уведомление со скрытой ссылкой."""
    from html import escape
    from urllib.parse import urlparse

    discipline = escape(task["discipline"])
    module = escape(task["module"])
    task_type = escape(task["type"])

    message = (
        f"🟢 {discipline}\n"
        f"{module}\n"
        f"{task_type} — открылся!"
    )

    url = task.get("url")

    if url:
        parsed = urlparse(url)

        # Разрешаем только ссылки на Практикум
        if (
            parsed.scheme == "https"
            and parsed.hostname == "practicum.yandex.ru"
            and not parsed.username
            and not parsed.password
        ):
            clean_url = parsed._replace(
                query="",
                fragment="",
            ).geturl()

            message += (
                f'\n\n🔗 <a href="{escape(clean_url, quote=True)}">'
                "Ссылка</a>"
            )

    return message


def check_tasks(tasks):
    """Обновляет статусы и сохраняет новые открытия в очередь."""
    opened = []

    with get_connection() as connection:
        for task in tasks:
            previous = connection.execute(
                "SELECT locked FROM tasks WHERE id = ?",
                (task["id"],),
            ).fetchone()

            # Задание раньше было закрыто, теперь открыто
            if (
                previous is not None
                and bool(previous[0])
                and not task["locked"]
            ):
                opened.append(task)

                connection.execute(
                    """
                    INSERT OR IGNORE INTO notifications (
                        task_id, message
                    )
                    VALUES (?, ?)
                    """,
                    (
                        task["id"],
                        format_notification(task),
                    ),
                )

            connection.execute(
                """
                INSERT INTO tasks (
                    id,
                    discipline,
                    module,
                    type,
                    status,
                    locked,
                    url
                )
                VALUES (?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    discipline = excluded.discipline,
                    module = excluded.module,
                    type = excluded.type,
                    status = excluded.status,
                    locked = excluded.locked,
                    url = excluded.url
                """,
                (
                    task["id"],
                    task["discipline"],
                    task["module"],
                    task["type"],
                    task["status"],
                    int(task["locked"]),
                    task.get("url"),
                ),
            )

    return opened


def get_pending_notifications():
    """Возвращает все неотправленные уведомления."""
    with get_connection() as connection:
        return connection.execute(
            """
            SELECT task_id, message
            FROM notifications
            WHERE sent = 0
            """
        ).fetchall()


def mark_notification_sent(task_id):
    """Помечает уведомление отправленным."""
    with get_connection() as connection:
        connection.execute(
            """
            UPDATE notifications
            SET sent = 1
            WHERE task_id = ?
            """,
            (task_id,),
        )
