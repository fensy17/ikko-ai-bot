import os
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

load_dotenv()

from ai_agent import ask_agent
from iiko_api import IikoClient

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")

if not TELEGRAM_TOKEN:
    raise ValueError("Не задан TELEGRAM_TOKEN")

iiko = IikoClient()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "AI-ассистент iiko запущен.\n\n"
        "Команды:\n"
        "/start — запуск\n"
        "/iiko — проверить подключение к iiko\n"
        "/orgs — показать организации\n"
        "/menu — показать номенклатуру\n"
        "/stoplist — показать стоп-лист\n\n"
        "Также можно писать обычным текстом."
    )

async def iiko_check(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        data = iiko.get_organizations()
        orgs = data.get("organizations", [])

        if not orgs:
            await update.message.reply_text("iiko подключен, но организации не найдены.")
            return

        text = "iiko Cloud API подключен.\n\nОрганизации:\n"

        for org in orgs:
            text += f"- {org.get('name')} | ID: {org.get('id')}\n"

        await update.message.reply_text(text[:4000])

    except Exception as e:
        await update.message.reply_text(f"Ошибка iiko API: {e}")

async def orgs_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        data = iiko.get_organizations()
        orgs = data.get("organizations", [])

        if not orgs:
            await update.message.reply_text("Организации не найдены.")
            return

        text = "Организации:\n\n"

        for org in orgs:
            text += f"- {org.get('name')} |




