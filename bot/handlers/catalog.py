from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import CallbackQueryHandler, ContextTypes, MessageHandler, filters
from bot.storage import Storage
from bot.keyboards import (
    items_keyboard,
    main_menu_reply_keyboard,
    product_keyboard,
    back_to_menu_reply_keyboard,
    gold_quantity_keyboard, back_to_main_inline_keyboard, main_menu_inline_keyboard
)
from bot.handlers.cart import view_cart
from PIL import Image
from io import BytesIO

img_path = "assets/fyp.jpg"
db = Storage()
user_states = {}

async def show_item(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Универсальный обработчик товаров"""
    query = update.callback_query
    await query.answer()
    try:
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

async def show_catalog_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик кнопки Standoff 2 GOLD через callback"""
    query = update.callback_query
    await query.answer()
    try:
        all_items = db.get_products()
        gold_item = next((item for item in all_items if item['category'] == 'gold'), None)
        if not gold_item:
            await query.edit_message_text("❌ Товар не найден")
            return
        user_id = query.from_user.id
        user_states[user_id] = {
            'item_id': gold_item['id'],
            'category': 'gold',
            'price': gold_item['price'],
            'name': gold_item['name']
        }
        await query.edit_message_text(
            f"🟡<b>{gold_item['name']}</b>🟡\n\n"
            f"💰 Цена за единицу: <code>{gold_item['price']} BYN</code>\n\n"
            f"➡️ <b>Введите количество голды (минимум 100):</b>",
            parse_mode="HTML",
            reply_markup=gold_quantity_keyboard()
        )
    except Exception as e:
        await query.edit_message_text(f"⚠️ Ошибка загрузки: {str(e)}")

async def show_catalog_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик кнопки Standoff 2 GOLD через сообщение"""
    try:
        all_items = db.get_products()
        gold_item = next((item for item in all_items if item['category'] == 'gold'), None)
        if not gold_item:
            await update.message.reply_text("❌ Товар не найден", reply_markup=main_menu_inline_keyboard())
            return
        user_id = update.message.from_user.id
        user_states[user_id] = {
            'item_id': gold_item['id'],
            'category': 'gold',
            'price': gold_item['price'],
            'name': gold_item['name']
        }
        await context.bot.send_message(
            chat_id=update.message.chat_id,
            text=f"🟡<b>{gold_item['name']}</b>🟡\n\n"
                 f"💰 Цена за единицу: <code>{gold_item['price']} BYN</code>\n\n"
                 f"➡️ <b>Введите количество голды (минимум 100):</b>",
            parse_mode="HTML",
            reply_markup=gold_quantity_keyboard()
        )
    except Exception as e:
        await update.message.reply_text(f"⚠️ Ошибка загрузки: {str(e)}", reply_markup=main_menu_inline_keyboard())

async def show_catalog_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик кнопки Standoff 2 GOLD через сообщение"""
    try:
        all_items = db.get_products()
        gold_item = next((item for item in all_items if item['category'] == 'gold'), None)
        if not gold_item:
            await update.message.reply_text("❌ Товар не найден")
            return
        user_id = update.message.from_user.id
        user_states[user_id] = {
            'item_id': gold_item['id'],
            'category': 'gold',
            'price': gold_item['price'],
            'name': gold_item['name']
        }
        await update.message.reply_text(
            f"🟡<b>{gold_item['name']}</b>🟡\n\n"
            f"💰 Цена за единицу: <code>{gold_item['price']} BYN</code>\n\n"
            f"➡️ <b>Введите количество голды (минимум 100):</b>",
            parse_mode="HTML",
            reply_markup=gold_quantity_keyboard()
        )
    except Exception as e:
        await update.message.reply_text(f"⚠️ Ошибка загрузки: {str(e)}")

async def handle_gold_confirmation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик подтверждения добавления gold в корзину"""
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    if user_id not in user_states or 'quantity' not in user_states[user_id]:
        await query.answer("❌ Сессия устарела. Начните заново.", show_alert=True)
        await query.edit_message_text("❌ Сессия устарела", reply_markup=main_menu_reply_keyboard())
        return
    if query.data == "confirm_gold":
        await query.answer("✅ Gold добавлен в корзину!")
        item_info = user_states[user_id]
        cart = db.get_cart(user_id)
        if "items" not in cart:
            cart["items"] = []
        cart["items"].extend([item_info['item_id']] * item_info['quantity'])
        db.save_cart(user_id, cart)
        await query.edit_message_text(
            f"✅ Добавлено {item_info['quantity']} gold в корзину!",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🛒 Корзина", callback_data="view_cart")],
                [InlineKeyboardButton("◀️ Назад", callback_data="to_main_menu")],
            ])
        )
    else:
        await query.answer("❌ Добавление отменено")
        await query.edit_message_text(
            "❌ Добавление отменено",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("◀️ Назад", callback_data="to_main_menu")],
            ])
        )
    del user_states[user_id]

async def handle_gold_quantity(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик ввода количества gold"""
    user_id = update.message.from_user.id
    if user_id not in user_states:
        return
    try:
        quantity = int(update.message.text)
        if quantity < 100:
            await update.message.reply_text("❌ Количество должно быть больше 100")
            return
        if quantity > 1000000:
            await update.message.reply_text("❌ Слишком большое количество")
            return
        item_info = user_states[user_id]
        total_price = item_info['price'] * quantity
        user_states[user_id]['quantity'] = quantity
        user_states[user_id]['total_price'] = total_price
        await update.message.reply_text(
            f"✅ <b>Подтверждение заказа</b>\n\n"
            f"🟡Товар: <b>{item_info['name']}</b>🟡\n"
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
        pass

async def handle_gold_confirmation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик подтверждения добавления gold в корзину"""
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    if query.data == "cancel_gold":
        await query.answer("❌ Добавление отменено")
        img = Image.open(img_path)
        img_buffer = BytesIO()
        img.save(img_buffer, format="JPEG")
        img_buffer.seek(0)

        await query.message.reply_text(
            "❌ Добавление отменено",
            reply_markup=main_menu_reply_keyboard()
        )
        await query.message.delete()
        if user_id in user_states:
            del user_states[user_id]
        return
    if user_id not in user_states or 'quantity' not in user_states[user_id]:
        await query.answer("❌ Сессия устарела. Начните заново.", show_alert=True)
        img = Image.open(img_path)
        img_buffer = BytesIO()
        img.save(img_buffer, format="JPEG")
        img_buffer.seek(0)
        await query.message.reply_text(
            "❌ Сессия устарела",
            reply_markup=main_menu_reply_keyboard()
        )
        await query.message.delete()
        return
    if query.data == "confirm_gold":
        await query.answer("✅ Gold добавлен в корзину!")
        item_info = user_states[user_id]
        cart = db.get_cart(user_id)
        if "items" not in cart:
            cart["items"] = []
        cart["items"].extend([item_info['item_id']] * item_info['quantity'])
        db.save_cart(user_id, cart)

        await query.edit_message_text(
            f"✅ Добавлено {item_info['quantity']} gold в корзину!",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🛒 Корзина", callback_data="view_cart")],
            ])
        )
        del user_states[user_id]

async def show_options_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик кнопки TG-Premium через callback"""
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

async def show_options_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик кнопки TG-Premium через сообщение"""
    try:
        all_items = db.get_products()
        premium_items = [item for item in all_items if item['category'] == 'premium']
        await update.message.reply_text(
            "💎 ✨Tg premium✨",
            reply_markup=items_keyboard(premium_items, 'premium')
        )
    except Exception as e:
        await update.message.reply_text(f"⚠️ Ошибка загрузки услуг: {str(e)}")

async def add_to_cart(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Добавление товара в корзину (для premium)"""
    query = update.callback_query
    await query.answer("✅ Товар добавлен в корзину!")
    try:
        item_id = int(query.data.split('_')[1])
        user_id = query.from_user.id
        cart = db.get_cart(user_id)
        if "items" not in cart:
            cart["items"] = []
        cart["items"].append(item_id)
        db.save_cart(user_id, cart)
        item = next((i for i in db.get_products() if i['id'] == item_id), None)
        if item:
            await query.edit_message_reply_markup(reply_markup=product_keyboard(item_id, item['category']))
    except Exception as e:
        await query.answer(f"❌ Ошибка: {str(e)}")

async def show_review_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик кнопки Отзывы через callback"""
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(
        f"<b>А здесь вы можете посмотреть или оставить отзывы</b> 👇\n"
        f"<b>Отзывы: https://t.me/zyg0o_info/11</b>",
        parse_mode="HTML",
        reply_markup=back_to_menu_reply_keyboard()
    )

async def show_review_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик кнопки Отзывы через сообщение"""
    await update.message.reply_text(
        f"<b>А здесь вы можете посмотреть или оставить отзывы</b> 👇\n"
        f"<b>Отзывы: https://t.me/zyg0o_info/11</b>",
        parse_mode="HTML",
        reply_markup=back_to_menu_reply_keyboard()
    )

async def handle_back(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик кнопки назад"""
    query = update.callback_query
    await query.answer()
    try:
        category = query.data.split('_')[1]
        if category == 'gold':
            await back_to_main_callback(update, context)
        elif category == 'premium':
            await show_options_callback(update, context)
        else:
            await back_to_main_callback(update, context)
    except:
        await back_to_main_callback(update, context)

async def back_to_main_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Возврат в главное меню через callback"""
    query = update.callback_query
    await query.answer()

    img = Image.open(img_path)
    img_buffer = BytesIO()
    img.save(img_buffer, format="JPEG")
    img_buffer.seek(0)

    await query.message.reply_photo(photo=img_buffer)
    await query.message.reply_text(
        f"\nДобро пожаловать в главное меню ZUGshop! Это бот для покупки голды в standoff 2 и ТГ-премиума. \n \nДля взаимодействия с ботом используй кнопки. \n \n Если возникнут вопросы пиши в поддержку @zyg0o.",
        reply_markup=main_menu_reply_keyboard()
    )
    await query.message.delete()

async def back_to_main_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Возврат в главное меню через сообщение"""
    img = Image.open(img_path)
    img_buffer = BytesIO()
    img.save(img_buffer, format="JPEG")
    img_buffer.seek(0)
    await update.message.reply_photo(
        photo=img_buffer
    )
    await update.message.reply_text(
        f"\nДобро пожаловать в главное меню ZUGshop! Это бот для покупки голды в standoff 2 и ТГ-премиума. \n \nДля взаимодействия с ботом используй кнопки. \n \n Если возникнут вопросы пиши в поддержку @zyg0o.",
        reply_markup=main_menu_reply_keyboard()
    )


async def handle_menu_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик нажатий на обычные кнопки"""
    from bot.handlers.cart import view_cart_message  # Добавьте импорт

    text = update.message.text
    if text == "💰 Standoff 2 GOLD":
        await show_catalog_message(update, context)
    elif text == "💎 TG-Premium":
        await show_options_message(update, context)
    elif text == "🛒 Корзина":
        await view_cart_message(update, context)  # Используем новую функцию
    elif text == "⭐ Отзывы":
        await show_review_message(update, context)
    elif text == "🏠 Главное меню":
        await back_to_main_message(update, context)
async def back_to_main_after_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик кнопки Главное меню после отмены"""
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(
        f"\nДобро пожаловать в главное меню ZUGshop! Это бот для покупки голды в standoff 2 и ТГ-премиума. \n \nДля взаимодействия с ботом используй кнопки. \n \n Если возникнут вопросы пиши в поддержку.",
        reply_markup=main_menu_reply_keyboard()
    )

catalog_handlers = [
    CallbackQueryHandler(show_catalog_callback, pattern="^catalog$"),
    CallbackQueryHandler(show_options_callback, pattern="^options$"),
    CallbackQueryHandler(show_item, pattern="^item_"),
    CallbackQueryHandler(add_to_cart, pattern="^add_"),
    CallbackQueryHandler(handle_back, pattern="^back_"),
    CallbackQueryHandler(back_to_main_callback, pattern="^to_main_menu$"),
    CallbackQueryHandler(back_to_main_after_cancel, pattern="^to_main_menu_after_cancel$"),
    CallbackQueryHandler(handle_gold_confirmation, pattern="^(confirm_gold|cancel_gold|to_main_menu_after_cancel)$"),
    CallbackQueryHandler(view_cart, pattern="^view_cart$"),
    CallbackQueryHandler(show_review_callback, pattern="^show_review"),
    MessageHandler(filters.TEXT & ~filters.COMMAND & filters.Regex(r'^\d+$'), handle_gold_quantity),
    MessageHandler(filters.TEXT & ~filters.COMMAND, handle_menu_buttons)
]
