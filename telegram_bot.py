
import os

import requests
from dotenv import load_dotenv

load_dotenv()


def send_message(text: str) -> None:
    token = os.getenv("BOT_TOKEN")
    chat_id = os.getenv("CHAT_ID")

    if not token or not chat_id:
        raise RuntimeError("BOT_TOKEN или CHAT_ID отсутствует в .env")

    response = requests.post(
        f"https://api.telegram.org/bot{token}/sendMessage",
        json={
            "chat_id": chat_id,
            "text": text,
            "parse_mode": "HTML",
        },
        timeout=15,
    )

    response.raise_for_status()

    result = response.json()
    if not result.get("ok"):
        raise RuntimeError(f"Ошибка Telegram: {result}")


def format_notification(task: dict) -> str:
    discipline = task["discipline"]
    module = task["module"]
    task_type = task["type"]

    return (
        f"🟢 {discipline}\n"
        f"{module}. {task_type} — открылся!"
    )


if __name__ == "__main__":
    from parser import get_tasks

    tasks = get_tasks()

    if not tasks:
        raise RuntimeError("Не удалось получить задания")

    from database import get_connection

    with get_connection() as connection:
        opened_count = connection.execute(
            "SELECT COUNT(*) FROM tasks WHERE locked = 0"
            " AND id NOT IN (SELECT id FROM tasks WHERE locked = 1)"
        ).fetchone()[0]

    message = (
        f"Всего найдено: {len(tasks)}\n"
        f"Закрытых: {sum(task['locked'] for task in tasks)}\n"
        f"Новых открытий: 0"
    )

    send_message(message)
    print("Статистика отправлена в Telegram!")

