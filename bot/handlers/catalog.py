from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import CallbackQueryHandler, ContextTypes, MessageHandler, filters
from bot.handlers.cart import view_cart
from bot.storage import Storage
from bot.keyboards import (
    items_keyboard,
    main_menu_keyboard,
    product_keyboard,
    back_to_menu_keyboard
)

db = Storage()

# Глобальная переменная для хранения состояния
user_states = {}


async def show_item(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Универсальный обработчик товаров"""
    query = update.callback_query
    await query.answer()

    try:
        # Формат: item_{category}_{id}
        parts = query.data.split('_')
        if len(parts) < 3:
            await query.edit_message_text("❌ Неверный формат запроса")
            return

        category = parts[1]
        item_id = int(parts[2])

        item = next((i for i in db.get_products() if i['id'] == item_id and i['category'] == category), None)
        if not item:
            await query.edit_message_text("❌ Услуга не найдена")
            return

        # Для ВСЕХ товаров показываем стандартную карточку
        text = (
            f"<b>{item.get('name', 'Услуга')}</b>\n\n"
            f"💰 Цена: <code>{item['price']} BYN</code>\n"
            f"📝 {item.get('description', 'Нет описания')}"
        )

        await query.edit_message_text(
            text,
            parse_mode="HTML",
            reply_markup=product_keyboard(item_id, category)
        )

    except Exception as e:
        await query.edit_message_text(f"⚠️ Ошибка: {str(e)}")


async def show_catalog(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик кнопки Standoff 2 GOLD - сразу запрашиваем количество"""
    query = update.callback_query
    await query.answer()

    try:
        all_items = db.get_products()
        gold_item = next((item for item in all_items if item['category'] == 'gold'), None)

        if not gold_item:
            await query.edit_message_text("❌ Товар не найден")
            return

        # Сохраняем информацию о товаре для этого пользователя
        user_id = query.from_user.id
        user_states[user_id] = {
            'item_id': gold_item['id'],
            'category': 'gold',
            'price': gold_item['price'],
            'name': gold_item['name']
        }

        await query.edit_message_text(
            f"🪙 <b>{gold_item['name']}</b>\n\n"
            f"💰 Цена за единицу: <code>{gold_item['price']} BYN</code>\n\n"
            f"➡️ <b>Введите количество голды которое хотите купить:</b>",
            parse_mode="HTML",
            reply_markup=back_to_menu_keyboard()
        )

    except Exception as e:
        await query.edit_message_text(f"⚠️ Ошибка загрузки: {str(e)}")

async def handle_gold_quantity(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик ввода количества gold"""
    user_id = update.message.from_user.id

    if user_id not in user_states:
        await update.message.reply_text("❌ Сначала выберите товар из меню")
        return

    try:
        quantity = int(update.message.text)
        if quantity <= 0:
            await update.message.reply_text("❌ Количество должно быть больше 0")
            return
        if quantity > 10000:
            await update.message.reply_text("❌ Слишком большое количество")
            return

        item_info = user_states[user_id]
        total_price = item_info['price'] * quantity

        # Сохраняем количество для добавления в корзину
        user_states[user_id]['quantity'] = quantity
        user_states[user_id]['total_price'] = total_price

        await update.message.reply_text(
            f"✅ <b>Подтверждение заказа</b>\n\n"
            f"🪙 Товар: <b>{item_info['name']}</b>\n"
            f"📦 Количество: <b>{quantity} голды</b>\n"
            f"💰 Цена за единицу: <code>{item_info['price']} BYN</code>\n"
            f"💵 Итого: <code>{total_price} BYN</code>\n\n"
            f"➡️ <b>Добавить в корзину?</b>",
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("✅ Да, добавить", callback_data="confirm_gold")],
                [InlineKeyboardButton("❌ Отмена", callback_data="cancel_gold")]
            ])
        )

    except ValueError:
        await update.message.reply_text("❌ Пожалуйста, введите число")


async def handle_gold_confirmation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик подтверждения добавления gold в корзину"""
    query = update.callback_query
    user_id = query.from_user.id

    if user_id not in user_states or 'quantity' not in user_states[user_id]:
        await query.answer("❌ Ошибка: данные не найдены")
        await query.edit_message_text("❌ Ошибка: данные не найдены")
        return

    if query.data == "confirm_gold":
        # Показываем алерт ТОЛЬКО при подтверждении
        await query.answer("✅ Товар добавлен в корзину!")

        item_info = user_states[user_id]

        # Добавляем товар в корзину quantity раз
        for _ in range(item_info['quantity']):
            db.add_to_cart(user_id, item_info['item_id'])

        # Очищаем состояние
        del user_states[user_id]

        await query.edit_message_text(
            f"✅ <b>Добавлено в корзину!</b>\n\n"
            f"🪙 {item_info['name']}\n"
            f"📦 Количество: {item_info['quantity']} Голды\n"
            f"💵 Сумма: {item_info['total_price']} BYN",
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🛒 Корзина", callback_data="view_cart")],
                [InlineKeyboardButton("🏠 Главное меню", callback_data="to_main_menu")]
            ])
        )
    else:
        # При отмене показываем другой алерт
        await query.answer("❌ Добавление отменено")

        # Очищаем состояние
        del user_states[user_id]

        await query.edit_message_text(
            "❌ Добавление отменено",
            reply_markup=main_menu_keyboard()
        )


async def show_options(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    try:
        all_items = db.get_products()
        premium_items = [item for item in all_items if item['category'] == 'premium']
        await query.edit_message_text(
            "💎 ✨Tg premium✨",
            reply_markup=items_keyboard(premium_items, 'premium')
        )
    except Exception as e:
        await query.edit_message_text(f"⚠️ Ошибка загрузки услуг: {str(e)}")


async def add_to_cart(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Добавление товара в корзину (для premium)"""
    query = update.callback_query
    await query.answer("✅ Товар добавлен в корзину!")

    try:
        item_id = int(query.data.split('_')[1])
        user_id = query.from_user.id

        db.add_to_cart(user_id, item_id)

        # Находим товар для получения категории
        item = next((i for i in db.get_products() if i['id'] == item_id), None)
        if item:
            await query.edit_message_reply_markup(
                reply_markup=product_keyboard(item_id, item['category'])
            )

    except Exception as e:
        await query.answer(f"❌ Ошибка: {str(e)}")


async def ask_consultant(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик кнопки консультанта"""
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(
        "💡 Задайте ваш вопрос консультанту...",
        reply_markup=back_to_menu_keyboard()
    )


async def handle_back(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик кнопки назад"""
    query = update.callback_query
    await query.answer()

    try:
        category = query.data.split('_')[1]
        if category == 'gold':
            await back_to_main(update, context)
        elif category == 'premium':
            await show_options(update, context)
        else:
            await back_to_main(update, context)
    except:
        await back_to_main(update, context)


async def back_to_main(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Возврат в главное меню"""
    query = update.callback_query
    await query.answer()

    await query.edit_message_text(#добавить сюда картинку
        f"\nДобро пожаловать в главное меню ZUGshop! Это бот для покупки голды в standoff 2 и ТГ-премиума. \n \nДля взаимодействия с ботом используй кнопки. \n \n Если возникнут вопросы пиши в поддержку.",
        reply_markup=main_menu_keyboard()
    )


catalog_handlers = [
    CallbackQueryHandler(show_catalog, pattern="^catalog$"),  # Только для gold
    CallbackQueryHandler(show_options, pattern="^options$"),  # Только для premium
    CallbackQueryHandler(show_item, pattern="^item_"),  # Для отдельных товаров
    CallbackQueryHandler(add_to_cart, pattern="^add_"),  # Добавление в корзину
    CallbackQueryHandler(handle_back, pattern="^back_"),  # Назад
    CallbackQueryHandler(back_to_main, pattern="^to_main_menu$"),
    CallbackQueryHandler(ask_consultant, pattern="^ask_consultant$"),
    CallbackQueryHandler(handle_gold_confirmation, pattern="^(confirm_gold|cancel_gold)$"),
    CallbackQueryHandler(view_cart, pattern="^view_cart$"),
    MessageHandler(filters.TEXT & ~filters.COMMAND, handle_gold_quantity),
]