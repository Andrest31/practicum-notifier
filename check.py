
from datetime import datetime

from database import (
    check_tasks,
    get_pending_notifications,
    mark_notification_sent,
)
from parser import get_tasks
from telegram_bot import send_message


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
