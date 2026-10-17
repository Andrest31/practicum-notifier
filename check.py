
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
from lock import AlreadyRunningError, single_instance
from parser import get_tasks
from telegram_bot import send_message

MIN_TASK_RATIO = 0.8


def validate_task_count(tasks):
    """Защита от неполной загрузки заданий."""
    with get_connection() as connection:
        previous_count = connection.execute(
            "SELECT COUNT(*) FROM tasks"
        ).fetchone()[0]

    current_count = len(tasks)

    if previous_count == 0:
        print(
            "Первый запуск: сравнение количества пропущено.",
            flush=True,
        )
        return

    print(
        f"Сравнение заданий: "
        f"было {previous_count}, "
        f"получено {current_count}",
        flush=True,
    )

    if current_count / previous_count < MIN_TASK_RATIO:
        raise RuntimeError(
            "Подозрительно мало заданий: "
            f"{current_count} из {previous_count}. "
            "SQLite не обновлена."
        )


def check_practicum():
    """Получает задания и обновляет их статусы."""
    print("Проверяем Практикум...", flush=True)

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


def send_pending():
    """Отправляет накопленные уведомления."""
    for task_id, message in get_pending_notifications():
        send_message(message)
        mark_notification_sent(task_id)

        print(f"Отправлено:\n{message}", flush=True)


def main():
    """Основной цикл одной проверки."""
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
            f"Ошибка проверки "
            f"({failures} подряд): {error}",
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
                    "Не удалось отправить предупреждение: "
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
                    "Не удалось отправить сообщение "
                    f"о восстановлении: {error}",
                    flush=True,
                )

            else:
                reset_health()

        elif failures:
            reset_health()

    # Отправляем уведомления о новых заданиях
    send_pending()

    print(
        "Ожидающих уведомлений: "
        f"{len(get_pending_notifications())}",
        flush=True,
    )


if __name__ == "__main__":
    try:
        with single_instance():
            main()

    except AlreadyRunningError:
        print(
            "⏳ Предыдущая проверка ещё выполняется. "
            "Пропускаем запуск.",
            flush=True,
        )
