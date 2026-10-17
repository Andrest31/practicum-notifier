
import re
from pathlib import Path

from playwright.sync_api import sync_playwright

PROFILE_DIR = Path("data/browser_profile").resolve()
URL = "https://practicum.yandex.ru/profile/higher-data-analytics/"


def normalize_discipline(name: str) -> str:
    """Очищает и сокращает название дисциплины."""
    name = re.sub(
        r"^\s*\[(?:МИФИ|Практикум)\]\s*",
        "",
        name,
        flags=re.I,
    )
    name = " ".join(name.split())

    lower_name = name.lower()

    if "теории вероятностей" in lower_name:
        return "Теор вер"

    if "математической статистики" in lower_name:
        return "Мат стат"

    if "машинное обучение с учителем" in lower_name:
        return "Машинное обучение"

    return name


def select_first_semester(page):
    """Находит и выбирает первый семестр."""
    print("Ищем первый семестр...")

    semester = page.get_by_text(
        re.compile(r"1\s*семестр", re.I),
        exact=False,
    ).last

    semester.wait_for(
        state="visible",
        timeout=30000,
    )

    semester.scroll_into_view_if_needed()
    semester.click(timeout=15000)

    print("Клик по первому семестру выполнен")


def get_tasks():
    """Получает задания первого семестра из Практикума."""
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch_persistent_context(
            user_data_dir=str(PROFILE_DIR),
            headless=True,
        )

        try:
            page = browser.pages[0] if browser.pages else browser.new_page()

            page.goto(
                URL,
                wait_until="domcontentloaded",
                timeout=30000,
            )

            select_first_semester(page)

            # Ждём появления карточек заданий
            page.locator(".control-form").first.wait_for(
                state="attached",
                timeout=30000,
            )

            tasks = page.locator(".control-form").evaluate_all(
                """elements => elements.map(el => {
                    const module = el.closest('li.module');
                    const discipline = el.closest('li.discipline-card');

                    const getText = (root, selector) =>
                        root?.querySelector(selector)
                            ?.textContent.trim() || '';

                    const moduleTitle = module
                        ? getText(
                            module,
                            'h1, h2, h3, h4, h5, h6'
                        )
                        : '';

                    const disciplineTitle = discipline
                        ? getText(
                            discipline,
                            'h1, h2, h3, h4, h5, h6'
                        )
                        : '';

                    const path = el.getAttribute('to');

                    return {
                        id: path,
                        discipline: disciplineTitle,
                        module: moduleTitle,
                        type: getText(el, '.control-form__name'),
                        status: getText(el, '.control-form__status'),
                        locked: Boolean(
                            el.querySelector(
                                '.control-form__status_no-access'
                            )
                        ),
                        url: path
                            ? new URL(path, location.origin).href
                            : null
                    };
                })"""
            )

            result = []

            for task in tasks:
                if not task["id"] or not task["type"]:
                    continue

                task["discipline"] = normalize_discipline(
                    task["discipline"]
                )

                result.append(task)

            print(f"Заданий получено: {len(result)}")

            return result

        finally:
            browser.close()


if __name__ == "__main__":
    tasks = get_tasks()

    print(f"\nВсего заданий: {len(tasks)}")

    for task in tasks:
        state = "🔒" if task["locked"] else "🔓"

        print(
            f"{state} {task['discipline']} | "
            f"{task['module']} | "
            f"{task['type']} | "
            f"{task['status']}"
        )

    print(
        f"\nЗакрытых: "
        f"{sum(task['locked'] for task in tasks)}"
    )
