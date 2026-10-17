
from database import get_connection


def main():
    with get_connection() as db:
        task = db.execute("""
            SELECT id, discipline, module, type
            FROM tasks
            WHERE locked = 0
              AND LOWER(type) LIKE '%проект%'
            LIMIT 1
        """).fetchone()

        if task is None:
            raise RuntimeError("Открытых проектов не найдено")

        task_id, discipline, module, task_type = task

        print(f"Выбрано: {discipline} | {module} | {task_type}")

        # Удаляем старое уведомление только для этого проекта
        db.execute(
            "DELETE FROM notifications WHERE task_id = ?",
            (task_id,),
        )

        # Имитируем закрытое состояние
        db.execute(
            """
            UPDATE tasks
            SET locked = 1,
                status = 'Скоро откроется'
            WHERE id = ?
            """,
            (task_id,),
        )

        print("Статус изменён на закрытый")
        print("История уведомления для проекта сброшена")


if __name__ == "__main__":
    main()
