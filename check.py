
from datetime import datetime

from database import (
    check_tasks,
    get_connection,
    get_pending_notifications,
    mark_notification_sent,
)
from parser import get_tasks
from telegram_bot import send_message

MIN_TASK_RATIO = 0.8


def validate_task_count(tasks):
    """Проверяет резкое уменьшение числа заданий."""
    with get_connection() as connection:
        previous_count = connection.execute(
            "SELECT COUNT(*) FROM tasks"
        ).fetchone()[0]

    current_count = len(tasks)

    if previous_count == 0:
        print("Первый запуск: сравнение количества пропущено.")
        return

    ratio = current_count / previous_count

    print(
        f"Сравнение заданий: "
        f"было {previous_count}, "
        f"получено {current_count}"
    )

    if ratio < MIN_TASK_RATIO:
        raise RuntimeError(
            "Подозрительно мало заданий: "
            f"{current_count} из {previous_count}. "
            "SQLite не обновлена."
        )


def main():
    print(
        f"\n=====\n"
        f"{datetime.now():%d.%m %H:%M}\n"
        f"=====",
        flush=True,
    )

    print("Проверяем Практикум...")

    tasks = get_tasks()

    if not tasks:
        raise RuntimeError(
            "Задания не получены. Проверка остановлена."
        )

    validate_task_count(tasks)

    opened = check_tasks(tasks)

    print(f"Всего найдено: {len(tasks)}")
    print(
        f"Закрытых: "
        f"{sum(task['locked'] for task in tasks)}"
    )
    print(f"Новых открытий: {len(opened)}")

    pending = get_pending_notifications()

    for task_id, message in pending:
        send_message(message)
        mark_notification_sent(task_id)

        print(f"Отправлено:\n{message}")

    print(
        f"Ожидающих уведомлений: "
        f"{len(get_pending_notifications())}"
    )


if __name__ == "__main__":
    main()
