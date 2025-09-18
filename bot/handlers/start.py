from telegram.ext import CommandHandler
from telegram import Update
from telegram.ext import ContextTypes
from bot.keyboards import main_menu_keyboard
from PIL import Image
from io import BytesIO

img_path = "assets/fyp.jpg"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    img = Image.open(img_path)
    img_buffer = BytesIO()
    img.save(img_buffer, format="JPEG")
    img_buffer.seek(0)
    await update.message.reply_photo(photo=img_buffer)
    await update.message.reply_text(
        f"\nДобро пожаловать в главное меню ZUGshop! Это бот для покупки голды в standoff 2 и ТГ-премиума. \n \nДля взаимодействия с ботом используй кнопки. \n \n Если возникнут вопросы пиши в поддержку @nick_username.",
        reply_markup=main_menu_keyboard()
    )
start_handlers = [CommandHandler("start", start)]
