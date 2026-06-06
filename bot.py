import os
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

load_dotenv()

from ai_agent import ask_agent
from iiko_api import IikoClient
from sales_report import (
    report_summary,
    top_sales,
    profit_sales,
    worst_sales,
    sales_analysis,
)

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")

if not TELEGRAM_TOKEN:
    raise ValueError("Не задан TELEGRAM_TOKEN")

iiko = IikoClient()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "AI-ассистент iiko запущен.\n\n"
        "Команды:\n"
        "/start — запуск\n"
        "/iiko — проверить подключение\n"
        "/orgs — организации\n"
        "/menu — номенклатура\n"
        "/products — товары\n"
        "/search название — поиск товара\n"
        "/stoplist — стоп-лист\n\n"
        "Отчёты Excel:\n"
        "/report — общая выручка\n"
        "/top — топ продаж\n"
        "/profit — самые прибыльные позиции\n"
        "/worst — слабые продажи\n"
        "/analysis — полный анализ\n\n"
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
            text += f"- {org.get('name')} | ID: {org.get('id')}\n"

        await update.message.reply_text(text[:4000])

    except Exception as e:
        await update.message.reply_text(f"Ошибка /orgs: {e}")

async def menu_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        data = iiko.get_nomenclature()
        products = data.get("products", [])

        if not products:
            await update.message.reply_text("Номенклатура не найдена.")
            return

        text = f"Номенклатура iiko: {len(products)} позиций\n\n"

        for item in products[:80]:
            name = item.get("name", "Без названия")
            item_type = item.get("type", "")
            text += f"- {name} ({item_type})\n"

        if len(products) > 80:
            text += f"\nПоказано 80 из {len(products)} позиций."

        await update.message.reply_text(text[:4000])

    except Exception as e:
        await update.message.reply_text(f"Ошибка /menu: {e}")

async def products_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        data = iiko.get_nomenclature()
        products = data.get("products", [])

        only_products = [
            item for item in products
            if item.get("type") == "Product"
        ]

        if not only_products:
            await update.message.reply_text("Товары не найдены.")
            return

        text = f"Товары: {len(only_products)} позиций\n\n"

        for item in only_products[:80]:
            text += f"- {item.get('name', 'Без названия')}\n"

        if len(only_products) > 80:
            text += f"\nПоказано 80 из {len(only_products)} товаров."

        await update.message.reply_text(text[:4000])

    except Exception as e:
        await update.message.reply_text(f"Ошибка /products: {e}")

async def search_command(update: Update, context: ContextType


s.DEFAULT_TYPE):
    try:
        query = " ".join(context.args).strip().lower()

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

        text = f"Найдено по запросу «{query}»: {len(found)}\n\n"

        for item in found[:50]:
            text += (
                f"- {item.get('name', 'Без названия')}\n"
                f"  ID: {item.get('id')}\n"
                f"  Тип: {item.get('type')}\n\n"
            )

        if len(found) > 50:
            text += f"Показано 50 из {len(found)} результатов."

        await update.message.reply_text(text[:4000])

    except Exception as e:
        await update.message.reply_text(f"Ошибка /search: {e}")

async def stoplist_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        data = iiko.get_stoplist()
        terminal_groups = data.get("terminalGroupStopLists", [])

        if not terminal_groups:
            await update.message.reply_text("Стоп-лист пуст или данные не найдены.")
            return

        text = "Стоп-лист:\n\n"
        found_items = 0

        for group in terminal_groups:
            items = group.get("items", [])

            for item in items:
                product_id = item.get("productId")
                balance = item.get("balance")
                text += f"- productId: {product_id}, остаток: {balance}\n"
                found_items += 1

        if found_items == 0:
            text = "Стоп-лист пуст."

        await update.message.reply_text(text[:4000])

    except Exception as e:
        await update.message.reply_text(f"Ошибка /stoplist: {e}")

async def report_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        await update.message.reply_text(report_summary()[:4000])
    except Exception as e:
        await update.message.reply_text(f"Ошибка /report: {e}")

async def top_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        await update.message.reply_text(top_sales()[:4000])
    except Exception as e:
        await update.message.reply_text(f"Ошибка /top: {e}")

async def profit_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        await update.message.reply_text(profit_sales()[:4000])
    except Exception as e:
        await update.message.reply_text(f"Ошибка /profit: {e}")

async def worst_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        await update.message.reply_text(worst_sales()[:4000])
    except Exception as e:
        await update.message.reply_text(f"Ошибка /worst: {e}")

async def analysis_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        await update.message.reply_text(sales_analysis()[:4000])
    except Exception as e:
        await update.message.reply_text(f"Ошибка /analysis: {e}")

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

    app.add_handler(CommandHandler("re


port", report_command))
    app.add_handler(CommandHandler("top", top_command))
    app.add_handler(CommandHandler("profit", profit_command))
    app.add_handler(CommandHandler("worst", worst_command))
    app.add_handler(CommandHandler("analysis", analysis_command))

    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chat))

    app.run_polling()

if __name__ == "__main__":
    main()




