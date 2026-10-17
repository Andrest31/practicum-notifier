
from pathlib import Path

from playwright.sync_api import sync_playwright

PROFILE_DIR = Path("data/browser_profile").resolve()
URL = "https://practicum.yandex.ru/profile/higher-data-analytics/"


def main():
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch_persistent_context(
            user_data_dir=str(PROFILE_DIR),
            headless=False,
            viewport={"width": 1440, "height": 900},
        )

        page = browser.pages[0] if browser.pages else browser.new_page()
        page.goto(URL, wait_until="domcontentloaded")
        page.wait_for_timeout(5000)

        print("\n=== ТЕКУЩАЯ СТРАНИЦА ===")
        print(page.url)

        print("\n=== КНОПКИ ===")
        for index, button in enumerate(page.locator("button").all()):
            text = button.inner_text().strip()
            aria = button.get_attribute("aria-label")

            if text or aria:
                print(f"{index}: text={text[:100]!r}, aria={aria!r}")

        print("\n=== ЗАДАНИЯ И СТАТУСЫ ===")
        for line in page.locator("body").inner_text().splitlines():
            if any(
                word in line.lower()
                for word in (
                    "ассесмент",
                    "проект",
                    "скоро откроется",
                    "домашнее задание",
                    "тест",
                )
            ):
                print(line.strip())

        input("\nНажми Enter для завершения...")
        browser.close()


if __name__ == "__main__":
    main()
