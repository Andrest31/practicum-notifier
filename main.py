import os

import requests
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")


def send_message(text: str) -> None:
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"

    response = requests.post(
        url,
        json={
            "chat_id": CHAT_ID,
            "text": text,
        },
        timeout=10,
    )

    response.raise_for_status()
    print("Сообщение отправлено!")


if __name__ == "__main__":
    send_message("🚀 Practicum Notifier запущен!")