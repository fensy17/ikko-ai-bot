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
        "/iiko — проверить подключение\n"
        "/orgs — организации\n"
        "/menu — номенклатура\n"
        "/products — товары\n"
        "/search название — поиск товара\n"
        "/stoplist — стоп-лист\n"
        "/sales — продажи, скоро\n"
        "/report — отчёт, скоро\n"
        "/createitem — создание товара, скоро\n\n"
        "Также можно писать обычным текстом."
    )

async def iiko_check(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        data = iiko.get_organizations()
        orgs = data.get("organizations", [])

        text = "iiko Cloud API подключен.\n\nОрганизации:\n"
        for org in orgs:
            text += f"- {org.get('name')} | ID: {org.get('id')}\n"

        await update.message.reply_text(text[:4000])
    except Exception as e:
        await update.message.reply_text(f"Ошибка iiko API: {e}")

async def orgs_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await iiko_check(update, context)

async def menu_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        data = iiko.get_nomenclature()
        products = data.get("products", [])

        text = f"Номенклатура: {len(products)} позиций\n\n"
        for item in products[:80]:
            text += f"- {item.get('name')} ({item.get('type')})\n"

        await update.message.reply_text(text[:4000])
    except Exception as e:
        await update.message.reply_text(f"Ошибка /menu: {e}")

async def products_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        data = iiko.get_nomenclature()
        products = data.get("products", [])

        text = "Товары:\n\n"
        count = 0

        for item in products:
            if item.get("type") == "Product":
                text += f"- {item.get('name')}\n"
                count += 1

            if count >= 80:
                break

        text += f"\nПоказано: {count}"
        await update.message.reply_text(text[:4000])
    except Exception as e:
        await update.message.reply_text(f"Ошибка /products: {e}")

async def search_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        query = " ".join(context.args).lower()

        if not query:
            await update.message.reply_text("Напиши так: /search моцарелла")
            return

        data = iiko.get_nomenclature()
        products = data.get("products", [])

        found = [
            item for item in products
            if query in item.get("name", "").lower()
        ]

        if not found:
            await update.message.reply_text("Ничего не найдено.")
            return

        text = f"Найдено по запросу «{query}»:\n\n"

        for item in found[:50]:
            text += (
                f"- {item.get('name')}\n"
                f"  ID: {item.get('id')}\n"
                f"  Тип: {item.get('type')}\n\n"
            )

        await update.message.reply_text(text[:4000])
    except Exception as e:
        await update.message.reply_text(f"Ошибка /search: {e}")

async def stoplist_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        data = iiko.get_stoplist()
        await update.message.reply_text(str(data)[:4000])
    except Exception as e:
        await update.message.reply_text(f"Ошибка /stoplist: {e}")

async def sales_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Команда /sales пока не


подключена.\n"
        "В текущей Cloud API документации нет прямого метода отчёта по выручке iiko Office.\n"
        "Для продаж, скорее всего, понадобится отдельный API отчётов, iikoWeb-отчёты или доступ к SQL Server."
    )

async def report_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Команда /report пока не подключена.\n"
        "Сейчас работают: /iiko, /orgs, /menu, /products, /search, /stoplist."
    )

async def createitem_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Создание товаров через текущий Cloud API пока не подключено.\n"
        "Сначала нужно найти в документации метод создания номенклатуры или подключаться к iiko Office/SQL локально."
    )

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
    app.add_handler(CommandHandler("orgs", orgs_command))
    app.add_handler(CommandHandler("menu", menu_command))
    app.add_handler(CommandHandler("products", products_command))
    app.add_handler(CommandHandler("search", search_command))
    app.add_handler(CommandHandler("stoplist", stoplist_command))
    app.add_handler(CommandHandler("sales", sales_command))
    app.add_handler(CommandHandler("report", report_command))
    app.add_handler(CommandHandler("createitem", createitem_command))

    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chat))

    app.run_polling()

if __name__ == "__main__":
    main()
