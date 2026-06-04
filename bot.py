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
        "/iiko — проверить подключение к iiko\n\n"
        "Можно писать обычным текстом:\n"
        "Покажи мои организации iiko\n"
        "Что ты умеешь?"
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

async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user_text = update.message.text
        answer = ask_agent(user_text)
        await update.message.reply_text(answer[:4000])

    except Exception as e:
        await update.message.reply_text(f"Ошибка ассистента: {e}")

def main():
    app = Application.builder().token(TELEGRAM_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("iiko", iiko_check))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chat))

    app.run_polling()

if __name__ == "__main__":
    main()
