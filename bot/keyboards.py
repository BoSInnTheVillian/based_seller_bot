from telegram import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

def main_menu_reply_keyboard():
    """Обычные кнопки для главного меню"""
    return ReplyKeyboardMarkup(
        [
            [KeyboardButton("💰 Standoff 2 GOLD"), KeyboardButton("💎 TG-Premium")],
            [KeyboardButton("🛒 Корзина"), KeyboardButton("⭐ Отзывы")],
            [KeyboardButton("🏠 Главное меню")]
        ],
        resize_keyboard=True
    )

def back_to_menu_reply_keyboard():
    """Обычные кнопки для возврата в меню"""
    return ReplyKeyboardMarkup(
        [
            [KeyboardButton("🏠 Главное меню")]
        ],
        resize_keyboard=True
    )

def main_menu_keyboard():
    """Инлайн-кнопки для главного меню"""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("💰 Standoff 2 GOLD", callback_data="catalog")],
        [InlineKeyboardButton("💎 TG-Premium", callback_data="options")],
        [InlineKeyboardButton("🛒 Корзина", callback_data="view_cart")],
        [InlineKeyboardButton("⭐ Отзывы", callback_data="show_review")]
    ])

def back_to_menu_keyboard():
    """Инлайн-кнопка для возврата в главное меню"""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🏠 Главное меню", callback_data="to_main_menu")]
    ])

def items_keyboard(items: list, category: str):
    """Инлайн-кнопки для списка товаров"""
    buttons = [
        [InlineKeyboardButton(
            f"{item['name']} {item['price']} BYN",
            callback_data=f"item_{category}_{item['id']}"
        )]
        for item in items
    ]
    buttons.extend([
        [InlineKeyboardButton("🔙 В главное меню", callback_data="to_main_menu")]
    ])
    return InlineKeyboardMarkup(buttons)
def main_menu_inline_keyboard():
    """Инлайн-кнопки для главного меню"""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("💰 Standoff 2 GOLD", callback_data="catalog")],
        [InlineKeyboardButton("💎 TG-Premium", callback_data="options")],
        [InlineKeyboardButton("🛒 Корзина", callback_data="view_cart")],
        [InlineKeyboardButton("⭐ Отзывы", callback_data="show_review")]
    ])

def back_to_main_inline_keyboard():
    """Инлайн-кнопка для возврата в главное меню"""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🏠 Главное меню", callback_data="to_main_menu")]
    ])

def gold_quantity_keyboard():
    """Инлайн-кнопка для отмены ввода количества голды"""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("❌ Отмена", callback_data="cancel_gold")]
    ])

def back_to_main_after_cancel_keyboard():
    """Инлайн-кнопка для возврата в главное меню после отмены"""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🏠 Главное меню", callback_data="to_main_menu")]
    ])
def product_keyboard(item_id: int, category: str):
    """Инлайн-кнопки для карточки товара"""
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("➕ Добавить в корзину", callback_data=f"add_{item_id}"),
            InlineKeyboardButton("🛒 Корзина", callback_data="view_cart")
        ],
        [
            InlineKeyboardButton("◀️ Назад", callback_data=f"back_{category}"),
            InlineKeyboardButton("🏠 Главная", callback_data="to_main_menu")
        ]
    ])

def cart_keyboard(cart_items: list):
    """Инлайн-кнопки для корзины"""
    buttons = []
    for item in cart_items:
        buttons.extend([
            [
                InlineKeyboardButton("➖", callback_data=f"decrease_{item['id']}"),
                InlineKeyboardButton(f"{item['name'][:15]}", callback_data=f"item_{item['id']}"),
                InlineKeyboardButton("➕", callback_data=f"increase_{item['id']}")
            ]
        ])
    buttons.extend([
        [
            InlineKeyboardButton("🗑 Очистить корзину", callback_data="clear_cart"),
            InlineKeyboardButton("🏠 Главная", callback_data="to_main_menu")
        ],
        [InlineKeyboardButton("💳 Оформить заказ", callback_data="checkout")]
    ])
    return InlineKeyboardMarkup(buttons)
