from io import BytesIO

from PIL import Image
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import CallbackQueryHandler, ContextTypes, CommandHandler
from bot.storage import Storage
from config.config import Config
db = Storage()

from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import CallbackQueryHandler, ContextTypes, CommandHandler
from bot.storage import Storage
from bot.keyboards import main_menu_keyboard, main_menu_reply_keyboard  # Добавляем импорт

db = Storage()
img_path = "assets/fyp.jpg"

async def confirm_payment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Подтверждение оплаты админом"""
    query = update.callback_query
    await query.answer()
    img = Image.open(img_path)
    img_buffer = BytesIO()
    img.save(img_buffer, format="JPEG")
    img_buffer.seek(0)
    # Формат: confirm_{user_id}_{amount}
    parts = query.data.split('_')
    if len(parts) < 3:
        await query.answer("❌ Ошибка формата")
        return

    user_id = int(parts[1])
    amount = parts[2]

    # Отправляем уведомление пользователю
    try:
        await context.bot.send_message(
            chat_id=user_id,
            text=f"✅ <b>Оплата подтверждена!</b>\n\n"
                 f"💳 Сумма: {amount} BYN\n"
                 f"🎮 Товар активирован!\n\n"
                 f"Спасибо за покупку! 🛒",
            parse_mode="HTML"
        )

        # Очищаем корзину пользователя
        db.save_cart(user_id, {"items": []})
        await context.bot.send_photo(
            chat_id=user_id,
            photo=img_buffer
        )
        # Отправляем СТАРТОВОЕ сообщение как после /start
        await context.bot.send_message(
            chat_id=user_id,
            text=f"\nДобро пожаловать в главное меню ZUGshop! Это бот для покупки голды в standoff 2 и ТГ-премиума. \n \nДля взаимодействия с ботом используй кнопки. \n \n Если возникнут вопросы пиши в поддержку @zyg0o.",
            reply_markup=main_menu_reply_keyboard()
        )

        await query.edit_message_text(
            f"✅ Оплата подтверждена для пользователя {user_id}\n"
            f"💰 Сумма: {amount} BYN"
        )

    except Exception as e:
        await query.answer(f"❌ Ошибка: {e}")


async def reject_payment(update: Update, context: ContextTypes.DEFAULT_TYPE):

    """Отклонение оплаты админом"""
    query = update.callback_query
    await query.answer()
    img = Image.open(img_path)
    img_buffer = BytesIO()
    img.save(img_buffer, format="JPEG")
    img_buffer.seek(0)
    parts = query.data.split('_')
    if len(parts) < 3:
        await query.answer("❌ Ошибка формата")
        return

    user_id = int(parts[1])
    amount = parts[2]

    # Отправляем уведомление пользователю
    try:
        await context.bot.send_message(
            chat_id=user_id,
            text=f"❌ <b>Оплата не подтверждена</b>\n\n"
                 f"💳 Сумма: {amount} BYN\n"
                 f"⚠️ Возможно, чек неверный или оплата не поступила\n\n"
                 f"Свяжитесь с поддержкой для уточнения",
            parse_mode="HTML"
        )

        await context.bot.send_photo(
            chat_id=user_id,
            photo=img_buffer
        )
        await context.bot.send_message(
            chat_id=user_id,
            text=f"\nДобро пожаловать в главное меню ZUGshop! Это бот для покупки голды в standoff 2 и ТГ-премиума. \n \nДля взаимодействия с ботом используй кнопки. \n \n Если возникнут вопросы пиши в поддержку @zyg0o.",
            reply_markup=m
        )

        await query.edit_message_text(
            f"❌ Оплата отклонена для пользователя {user_id}\n"
            f"💰 Сумма: {amount} BYN"
        )

    except Exception as e:
        await query.answer(f"❌ Ошибка: {e}")


async def admin_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Статистика для админа"""
    if update.message.from_user.id != Config.ADMIN_ID:
        return

    # Здесь можно добавить статистику
    await update.message.reply_text("📊 Статистика админа")


# Обработчики для админских команд
admin_handlers = [
    CallbackQueryHandler(confirm_payment, pattern="^confirm_"),
    CallbackQueryHandler(reject_payment, pattern="^reject_"),
    CommandHandler("stats", admin_stats)
]