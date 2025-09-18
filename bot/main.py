from telegram.ext import Application, MessageHandler, filters
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from config.config import Config
from bot.storage import Storage
from bot.handlers import (
    start_handlers,
    catalog_handlers,
    cart_handlers,
)
from bot.admin import admin_handlers
from bot.keyboards import main_menu_reply_keyboard

db = Storage()

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик получения фото чека"""
    try:
        user = update.message.from_user
        cart = db.get_cart(user.id)
        products = db.get_products()
        total = 0
        items_count = {}
        for item_id in cart.get("items", []):
            items_count[item_id] = items_count.get(item_id, 0) + 1
        for item_id, count in items_count.items():
            product = next((p for p in products if p["id"] == item_id), None)
            if product:
                total += product["price"] * count
        await update.message.reply_text(
            "✅ Чек получен! Ожидайте подтверждения оплаты.\n"
            "Обычно это занимает до 15 минут.",
            reply_markup=main_menu_reply_keyboard()
        )
        await context.bot.send_photo(
            chat_id=Config.ADMIN_ID,
            photo=update.message.photo[-1].file_id,
            caption=f"📸 Чек от @{user.username}\n"
                   f"👤 ID: {user.id}\n"
                   f"💵 Сумма: {total} BYN"
        )
        await context.bot.send_message(
            chat_id=Config.ADMIN_ID,
            text=f"Подтвердить оплату от @{user.username}?",
            reply_markup=InlineKeyboardMarkup([
                [
                    InlineKeyboardButton("✅ Подтвердить", callback_data=f"confirm_{user.id}_{total}"),
                    InlineKeyboardButton("❌ Отклонить", callback_data=f"reject_{user.id}_{total}")
                ]
            ])
        )
    except Exception as e:
        print(f"Ошибка обработки фото: {e}")
        await update.message.reply_text("❌ Ошибка обработки чека")

def main():
    app = Application.builder().token(Config.BOT_TOKEN).build()
    all_handlers = (
        start_handlers +
        catalog_handlers +
        cart_handlers +
        admin_handlers
    )
    for handler in all_handlers:
        app.add_handler(handler)
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    print("Бот запущен! ✅")
    app.run_polling()

if __name__ == "__main__":
    main()
