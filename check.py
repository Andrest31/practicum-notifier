
from database import check_tasks
from parser import get_tasks
from telegram_bot import format_notification, send_message


def main():
    print("Проверяем задания Практикума...")

    tasks = get_tasks()

    if not tasks:
        raise RuntimeError("Задания не получены. Проверка остановлена.")

    opened = check_tasks(tasks)

    print(f"Всего найдено: {len(tasks)}")
    print(f"Закрытых: {sum(task['locked'] for task in tasks)}")
    print(f"Новых открытий: {len(opened)}")

    for task in opened:
        message = format_notification(task)
        send_message(message)
        print(f"Отправлено: {message}")


if __name__ == "__main__":
    main()
