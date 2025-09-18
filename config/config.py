import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    GIGACHAT_MODEL = "GigaChat-max"  # Используем максимальную модель
    GIGACHAT_TEMPERATURE = 0.3  # Контроль креативности (0-1)
    GIGACHAT_MAX_TOKENS = 2048
    BOT_TOKEN = os.getenv("BOT_TOKEN")
    ADMIN_ID = os.getenv("ADMIN_ID")
