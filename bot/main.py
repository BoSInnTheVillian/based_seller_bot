from telegram.ext import Application
from config.config import Config
from bot.handlers import (
    start_handlers,
    catalog_handlers,
    cart_handlers,
)
import asyncio


def main():
    # Явно создаем event loop для PythonAnywhere
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    app = Application.builder().token(Config.BOT_TOKEN).build()

    all_handlers = (
            start_handlers +
            catalog_handlers +
            cart_handlers
    )

    for handler in all_handlers:
        app.add_handler(handler)

    print("🤖 Бот запущен на PythonAnywhere!")
    app.run_polling()


if __name__ == "__main__":
    main()