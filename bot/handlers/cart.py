from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import CallbackQueryHandler, ContextTypes
from bot.storage import Storage
from bot.keyboards import main_menu_reply_keyboard, back_to_menu_reply_keyboard
import random
from config.config import Config
db = Storage()

async def view_cart(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    cart = db.get_cart(user_id)
    products = db.get_products()
    items_count = {}
    for item_id in cart["items"]:
        items_count[item_id] = items_count.get(item_id, 0) + 1
    cart_items = []
    total = 0
    for item_id, count in items_count.items():
        product = next((p for p in products if p["id"] == item_id), None)
        if product:
            sum_price = product["price"] * count
            cart_items.append({
                "id": product["id"],
                "name": product["name"],
                "price": product["price"],
                "count": count,
                "sum": sum_price
            })
            total += sum_price
    text = "🛒 <b>Ваша корзина</b>\n━━━━━━━━━━━━━━\n"
    if not cart_items:
        text += "\n🎈 <i>Корзина пуста</i>\n"
    else:
        for item in cart_items:
            text += (
                f"\n<b>{item['name']}</b>\n"
                f"│\n"
                f"├ Цена: <code>{item['price']} BYN</code>\n"
                f"├ Количество: <b>{item['count']}</b>\n"
                f"└ Сумма: <code>{item['sum']} BYN</code>\n"
            )
    text += "━━━━━━━━━━━━━━\n"
    text += f"💳 <b>Итого: <code>{total} BYN</code></b>"
    keyboard = []
    for item in cart_items:
        keyboard.append([
            InlineKeyboardButton("➖", callback_data=f"decrease_{item['id']}"),
            InlineKeyboardButton(f"{item['name'][:15]}", callback_data=f"item_{item['id']}"),
            InlineKeyboardButton("➕", callback_data=f"increase_{item['id']}")
        ])
    if cart_items:
        keyboard.append([
            InlineKeyboardButton("🗑 Очистить корзину", callback_data="clear_cart"),
            InlineKeyboardButton("🏠 Главное меню", callback_data="to_main_menu")
        ])
        keyboard.append([
            InlineKeyboardButton("💳 Оформить заказ", callback_data="checkout")
        ])
    await query.edit_message_text(
        text,
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


async def view_cart_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик кнопки Корзина через сообщение"""
    user_id = update.message.from_user.id
    cart = db.get_cart(user_id)
    products = db.get_products()

    items_count = {}
    for item_id in cart.get("items", []):
        items_count[item_id] = items_count.get(item_id, 0) + 1

    cart_items = []
    total = 0
    for item_id, count in items_count.items():
        product = next((p for p in products if p["id"] == item_id), None)
        if product:
            sum_price = product["price"] * count
            cart_items.append({
                "id": product["id"],
                "name": product["name"],
                "price": product["price"],
                "count": count,
                "sum": sum_price
            })
            total += sum_price

    text = "🛒 <b>Ваша корзина</b>\n━━━━━━━━━━━━━━\n"
    if not cart_items:
        text += "\n🎈 <i>Корзина пуста</i>\n"
    else:
        for item in cart_items:
            text += (
                f"\n<b>{item['name']}</b>\n"
                f"│\n"
                f"├ Цена: <code>{item['price']} BYN</code>\n"
                f"├ Количество: <b>{item['count']}</b>\n"
                f"└ Сумма: <code>{item['sum']} BYN</code>\n"
            )
    text += "━━━━━━━━━━━━━━\n"
    text += f"💳 <b>Итого: <code>{total} BYN</code></b>"

    keyboard = []
    for item in cart_items:
        keyboard.append([
            InlineKeyboardButton("➖", callback_data=f"decrease_{item['id']}"),
            InlineKeyboardButton(f"{item['name'][:15]}", callback_data=f"item_{item['id']}"),
            InlineKeyboardButton("➕", callback_data=f"increase_{item['id']}")
        ])

    if cart_items:
        keyboard.append([
            InlineKeyboardButton("🗑 Очистить корзину", callback_data="clear_cart"),
            InlineKeyboardButton("🏠 Главное меню", callback_data="to_main_menu")
        ])
        keyboard.append([
            InlineKeyboardButton("💳 Оформить заказ", callback_data="checkout")
        ])

    await update.message.reply_text(
        text,
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
async def change_quantity(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    action, item_id = query.data.split('_')
    item_id = int(item_id)
    user_id = query.from_user.id
    cart = db.get_cart(user_id)
    if action == "increase":
        cart["items"].append(item_id)
        await query.answer("✅ Добавлен 1 товар")
    elif action == "decrease":
        for i, cart_item_id in enumerate(cart["items"]):
            if cart_item_id == item_id:
                cart["items"].pop(i)
                await query.answer("❌ Удалён 1 товар")
                break
    db.save_cart(user_id, cart)
    await view_cart(update, context)

async def clear_cart(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer("🗑 Корзина очищена!")
    user_id = query.from_user.id
    db.save_cart(user_id, {"items": []})
    await view_cart(update, context)

async def checkout(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Оформление заказа"""
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    cart = db.get_cart(user_id)
    products = db.get_products()
    items_count = {}
    for item_id in cart.get("items", []):
        items_count[item_id] = items_count.get(item_id, 0) + 1
    cart_items = []
    total = 0
    for item_id, count in items_count.items():
        product = next((p for p in products if p["id"] == item_id), None)
        if product:
            sum_price = product["price"] * count
            cart_items.append({
                "id": product["id"],
                "name": product["name"],
                "price": product["price"],
                "count": count,
                "sum": sum_price
            })
            total += sum_price
    if not cart_items:
        await query.answer("❌ Корзина пуста")
        return
    order_number = random.randint(100, 999)
    order_text = (
        f"🧾 <b>Заказ №{order_number}</b>\n\n"
        f"💳 <b>Итого к оплате:</b> {total} BYN\n\n"
        f"💳 <b>Оплата</b>\n"
        f"Перевод на BYN-карту {Config.CARD_NUMBER} ({Config.BANK_NAME})\n\n"
        f"После оплаты нажмите кнопку ниже и отправьте чек 🧾"
    )
    await query.edit_message_text(
        order_text,
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("📸 Отправить чек", callback_data="send_receipt")],
            [InlineKeyboardButton("◀️ Назад в корзину", callback_data="view_cart")],
            [InlineKeyboardButton("🏠 Главное меню", callback_data="to_main_menu")]
        ])
    )

async def handle_receipt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик отправки чека"""
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(
        "📸 <b>Отправьте скриншот или фото чека об оплате</b>\n\n"
        "• Сделайте скриншот перевода\n"
        "• Или сфотографируйте чек\n"
        "• Отправьте фото в этот чат",
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("◀️ Назад к заказу", callback_data="checkout")],
            [InlineKeyboardButton("🏠 Главное меню", callback_data="to_main_menu")]
        ])
    )

cart_handlers = [
    CallbackQueryHandler(view_cart, pattern="^view_cart$"),
    CallbackQueryHandler(change_quantity, pattern="^(increase|decrease)_"),
    CallbackQueryHandler(clear_cart, pattern="^clear_cart$"),
    CallbackQueryHandler(checkout, pattern="^checkout$"),
    CallbackQueryHandler(handle_receipt, pattern="^send_receipt$")
]
