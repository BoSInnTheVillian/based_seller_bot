from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from random import choice





def consultant_products_keyboard(products: list):
    """Клавиатура для товаров консультанта (3 кнопки + возврат)"""
    buttons = [
        [InlineKeyboardButton(
            f"📌 {p['name']}",
            callback_data=f"item_{p['id']}"
        )]
        for p in products[:3]  # Ограничиваем 3 товарами
    ]
    buttons.append([
        InlineKeyboardButton("🔙 В главное меню", callback_data="to_main_menu")
    ])
    return InlineKeyboardMarkup(buttons)

def main_menu_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(f"💰Standoff 2 GOLD💰", callback_data="catalog")],
        [InlineKeyboardButton(f"💎🌟TG-premium🌟💎", callback_data="options")],
        [InlineKeyboardButton("🛒 Корзина", callback_data="view_cart")]
    ])

def back_to_menu_keyboard():
    """Клавиатура с кнопкой возврата в главное меню"""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🏠 Главное меню", callback_data="to_main_menu")]
    ])
def calculation_keyboard():
    """Клавиатура с кнопкой возврата в главное меню"""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🏠 Главное меню", callback_data="to_main_menu")]
    ])

def items_keyboard(items: list, category: str):
    """Универсальная клавиатура для списка товаров с категорией"""
    buttons = [
        [InlineKeyboardButton(
            f" {item['name']} {item['price']}BYN",
            callback_data=f"item_{category}_{item['id']}"  # Добавляем категорию
        )]
        for item in items
    ]
    buttons.extend([
        [InlineKeyboardButton("🔙 В главное меню", callback_data="to_main_menu")]
    ])
    return InlineKeyboardMarkup(buttons)

def product_keyboard(item_id: int, category: str):
    """Универсальная клавиатура для товара с категорией"""
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
