
from uuid import uuid4

from database import (
    check_tasks,
    get_pending_notifications,
    mark_notification_sent,
)
from telegram_bot import send_message


def main():
    task = {
        "id": f"test-{uuid4()}",
        "discipline": "Машинное обучение",
        "module": "Модуль 6. ДЗ-1. Простой проект",
        "type": "Проект",
        "status": "Скоро откроется",
        "locked": True,
    }

    # Сначала задание закрыто
    check_tasks([task])
    print("1. Закрытое задание сохранено")

    # Имитируем открытие
    task["locked"] = False
    task["status"] = "Доступно"
    opened = check_tasks([task])

    print(f"2. Новых открытий: {len(opened)}")

    # Отправляем уведомления из очереди
    for task_id, message in get_pending_notifications():
        send_message(message)
        mark_notification_sent(task_id)
        print(f"3. Отправлено: {message}")


if __name__ == "__main__":
    main()
