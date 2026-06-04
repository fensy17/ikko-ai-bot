import os
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from openai import OpenAI
from dotenv import load_dotenv
from iiko_api import IikoClient

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

client = OpenAI(api_key=OPENAI_API_KEY)
iiko = IikoClient()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Бот запущен и работает.")

async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
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

    try:
        response = client.responses.create(
            model="gpt-5",
            input=user_text
        )

        await update.message.reply_text(response.output_text[:4000])

    except Exception as e:
        await update.message.reply_text(f"Ошибка: {str(e)}")

def main():
    app = Application.builder().token(TELEGRAM_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chat))
    app.add_handler(CommandHandler("iiko", iiko_check))

    app.run_polling()

if __name__ == "__main__":
    main()
