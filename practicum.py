
from pathlib import Path

from playwright.sync_api import sync_playwright

PROFILE_DIR = Path("data/browser_profile").resolve()
PRACTICUM_URL = "https://practicum.yandex.ru/profile/higher-data-analytics/"


def main():
    PROFILE_DIR.mkdir(parents=True, exist_ok=True)

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch_persistent_context(
            user_data_dir=str(PROFILE_DIR),
            headless=False,
            viewport={"width": 1440, "height": 900},
        )

        page = browser.pages[0] if browser.pages else browser.new_page()
        page.goto(PRACTICUM_URL, wait_until="domcontentloaded")

        print("Открой Практикум и авторизуйся, если потребуется.")
        print("После появления списка курсов вернись в терминал.")

        input("Нажми Enter для сохранения сессии и завершения...")

        print(f"Текущая страница: {page.url}")
        browser.close()
        print("Сессия браузера сохранена!")


if __name__ == "__main__":
    main()
