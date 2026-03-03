import os
import asyncio
import aiohttp
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
)

TOKEN = "7830152931:AAGe1xmx1BW_q9eIld3mDlg0eOBiziKmPmY"  # або встав токен

# -------- GLOBAL STATE --------
session: aiohttp.ClientSession | None = None
active_tasks = {}


# -------- INIT / SHUTDOWN --------
async def post_init(application):
    """Створюємо одну HTTP session для всього бота"""
    global session
    session = aiohttp.ClientSession()

    # прибирає 409 conflict після деплою
    await application.bot.delete_webhook(drop_pending_updates=True)


async def post_shutdown(application):
    """Закриваємо session при зупинці"""
    global session
    if session:
        await session.close()


# -------- BINANCE PRICE --------
async def get_price():
    global session

    url = "https://api.binance.com/api/v3/ticker/price?symbol=BONKUSDT"

    async with session.get(url, timeout=10) as response:
        data = await response.json()
        return float(data["price"])


# -------- COMMANDS --------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Привіт!\n"
        "/groshi — live ціна BONK\n"
        "/stop — зупинити"
    )


# -------- LIVE TRACKER --------
async def price_tracker(chat_id, message_id, context):
    last_text = None

    while True:
        try:
            price = await get_price()

            text = f"💰 BONK/USDT\n\nЦіна: {price}"

            # редагуємо тільки якщо змінилось
            if text != last_text:
                await context.bot.edit_message_text(
                    chat_id=chat_id,
                    message_id=message_id,
                    text=text,
                )
                last_text = text

            await asyncio.sleep(5)

        except asyncio.CancelledError:
            print("Tracker stopped")
            break

        except Exception as e:
            print("Tracker error:", e)
            await asyncio.sleep(5)


# -------- /groshi --------
async def groshi(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id

    if chat_id in active_tasks:
        await update.message.reply_text("⚠️ Вже запущено")
        return

    msg = await update.message.reply_text("⏳ Завантаження ціни...")

    task = asyncio.create_task(
        price_tracker(chat_id, msg.message_id, context)
    )

    active_tasks[chat_id] = task


# -------- /stop --------
async def stop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id

    task = active_tasks.get(chat_id)

    if task:
        task.cancel()
        del active_tasks[chat_id]
        await update.message.reply_text("🛑 Оновлення зупинено")
    else:
        await update.message.reply_text("Немає активного трекера")


# -------- MAIN --------
def main():
    app = (
        ApplicationBuilder()
        .token(TOKEN)
        .post_init(post_init)
        .post_shutdown(post_shutdown)
        .build()
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("groshi", groshi))
    app.add_handler(CommandHandler("stop", stop))

    print("Bot started...")
    app.run_polling()


if __name__ == "__main__":
    main()