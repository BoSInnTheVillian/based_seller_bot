import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    BOT_TOKEN = os.getenv("BOT_TOKEN")
    ADMIN_ID = os.getenv("ADMIN_ID")
    CARD_NUMBER = os.getenv("CARD_NUMBER")
    BANK_NAME = os.getenv("BANK_NAME")
