
from pathlib import Path

from playwright.sync_api import sync_playwright

PROFILE_DIR = Path("data/browser_profile").resolve()
URL = "https://practicum.yandex.ru/profile/higher-data-analytics/"


def main():
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch_persistent_context(
            user_data_dir=str(PROFILE_DIR),
            headless=False,
        )

        page = browser.pages[0] if browser.pages else browser.new_page()
        page.goto(URL, wait_until="domcontentloaded")

        page.get_by_text("Скоро откроется", exact=True).first.wait_for(
            timeout=20000
        )

        cards = page.get_by_text("Скоро откроется", exact=True)

        print(f"Найдено закрытых заданий: {cards.count()}")

        for index in range(min(cards.count(), 5)):
            element = cards.nth(index)

            print(f"\n=== ЗАДАНИЕ {index + 1} ===")

            html = element.evaluate(
                "(el) => el.parentElement.parentElement.outerHTML"
            )

            print(html[:4000])

        input("\nНажми Enter для завершения...")
        browser.close()


if __name__ == "__main__":
    main()
