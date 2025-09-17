from telegram.ext import Application

from bot.keyboards import main_menu_keyboard
from config.config import Config
from bot.handlers import (
    start_handlers,
    catalog_handlers,
    cart_handlers,
)
import asyncio
from telegram import Update
from telegram.ext import ContextTypes

# Для хранения состояния пользователей
user_states = {}


async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик получения фото чека"""
    user_id = update.message.from_user.id

    # Проверяем, ожидаем ли мы чек от этого пользователя
    if user_id in user_states and user_states[user_id].get('awaiting_receipt'):
        await update.message.reply_text(
            "✅ Чек получен! Ожидайте подтверждения оплаты.\n"
            "Обычно это занимает до 15 минут.",
            reply_markup=main_menu_keyboard()
        )
        # Очищаем состояние
        del user_states[user_id]
    else:
        await update.message.reply_text(
            "📸 Чтобы отправить чек, сначала оформите заказ через корзину",
            reply_markup=main_menu_keyboard()
        )

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