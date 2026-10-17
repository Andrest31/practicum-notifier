
from datetime import datetime

from database import (
    check_tasks,
    get_connection,
    get_pending_notifications,
    mark_notification_sent,
)
from health import (
    FAILURE_THRESHOLD,
    get_health,
    mark_alerted,
    record_failure,
    reset_health,
)
from parser import get_tasks
from telegram_bot import send_message

MIN_TASK_RATIO = 0.8


def validate_task_count(tasks):
    """Защита от резкого уменьшения количества заданий."""
    with get_connection() as connection:
        previous_count = connection.execute(
            "SELECT COUNT(*) FROM tasks"
        ).fetchone()[0]

    current_count = len(tasks)

    if previous_count == 0:
        return

    print(
        f"Сравнение заданий: "
        f"было {previous_count}, получено {current_count}"
    )

    if current_count / previous_count < MIN_TASK_RATIO:
        raise RuntimeError(
            f"Получено только {current_count} "
            f"из {previous_count} заданий."
        )


def check_practicum():
    """Проверяет сайт и обновляет базу."""
    print("Проверяем Практикум...", flush=True)

    tasks = get_tasks()

    if not tasks:
        raise RuntimeError("Список заданий пуст.")

    validate_task_count(tasks)

    opened = check_tasks(tasks)

    print(f"Всего найдено: {len(tasks)}")
    print(
        f"Закрытых: "
        f"{sum(task['locked'] for task in tasks)}"
    )
    print(f"Новых открытий: {len(opened)}")


def send_pending():
    """Отправляет ожидающие уведомления."""
    for task_id, message in get_pending_notifications():
        send_message(message)
        mark_notification_sent(task_id)
        print(f"Отправлено:\n{message}")


def main():
    print(
        f"\n=====\n"
        f"{datetime.now():%d.%m %H:%M}\n"
        f"=====",
        flush=True,
    )

    try:
        check_practicum()

    except Exception as error:
        failures, alerted = record_failure()

        print(
            f"Ошибка проверки ({failures} подряд): {error}",
            flush=True,
        )

        if failures >= FAILURE_THRESHOLD and not alerted:
            message = (
                "🔴 Ошибка проверки Практикума\n\n"
                f"Неудачных проверок подряд: {failures}\n"
                f"Причина: {str(error)[:500]}"
            )

            try:
                send_message(message)
            except Exception as telegram_error:
                print(
                    f"Не удалось отправить предупреждение: "
                    f"{telegram_error}",
                    flush=True,
                )
            else:
                mark_alerted()

        raise

    else:
        failures, alerted = get_health()

        if alerted:
            try:
                send_message(
                    "🟢 Практикум снова доступен!\n"
                    "Проверка заданий восстановлена."
                )
            except Exception as error:
                print(
                    f"Не удалось отправить сообщение "
                    f"о восстановлении: {error}",
                    flush=True,
                )
            else:
                reset_health()
        elif failures:
            reset_health()

    # Отправляем уведомления об открытии заданий
    send_pending()

    print(
        f"Ожидающих уведомлений: "
        f"{len(get_pending_notifications())}"
    )


if __name__ == "__main__":
    main()
