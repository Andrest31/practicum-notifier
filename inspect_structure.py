
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

        try:
            page = browser.pages[0] if browser.pages else browser.new_page()
            page.goto(URL, wait_until="domcontentloaded")

            page.locator(".control-form").first.wait_for(timeout=20000)

            result = page.locator(".control-form").first.evaluate(
                """el => {
                    const result = [];
                    let node = el;

                    for (let i = 0; i < 7 && node; i++) {
                        result.push({
                            level: i,
                            tag: node.tagName,
                            className: node.className,
                            text: (node.innerText || '')
                                .trim()
                                .slice(0, 500),
                            headings: Array.from(
                                node.querySelectorAll(
                                    'h1, h2, h3, h4, h5, h6'
                                )
                            ).map(h => h.innerText.trim())
                        });

                        node = node.parentElement;
                    }

                    return result;
                }"""
            )

            for item in result:
                print(f"\n=== УРОВЕНЬ {item['level']} ===")
                print("Тег:", item["tag"])
                print("Класс:", item["className"])
                print("Заголовки:", item["headings"])
                print("Текст:", item["text"])

        finally:
            browser.close()


if __name__ == "__main__":
    main()
