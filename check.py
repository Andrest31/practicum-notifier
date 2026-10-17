
from database import check_tasks
from parser import get_tasks


def main():
    print("Проверяем задания Практикума...")

    tasks = get_tasks()

    if not tasks:
        raise RuntimeError(
            "Не удалось получить задания. База не обновлена."
        )

    opened = check_tasks(tasks)

    print(f"Всего найдено: {len(tasks)}")
    print(f"Закрытых: {sum(task['locked'] for task in tasks)}")
    print(f"Новых открытий: {len(opened)}")

    for task in opened:
        print(
            f"\n🟢 {task['discipline']}\n"
            f"{task['module']}. {task['type']} — открылся!"
        )


if __name__ == "__main__":
    main()
