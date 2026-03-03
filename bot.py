import os
import asyncio
import aiohttp
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
)

TOKEN = "7830152931:AAGe1xmx1BW_q9eIld3mDlg0eOBiziKmPmY"  # або встав токен прямо

# зберігаємо активні задачі
active_tasks = {}


# --- Binance price ---
async def get_price():
    url = "https://api.binance.com/api/v3/ticker/price?symbol=BONKUSDT"

    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            data = await response.json()
            return float(data["price"])


# --- START ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Привіт!\n"
        "/groshi — live ціна BONK\n"
        "/stop — зупинити"
    )


# --- LIVE PRICE LOOP ---
async def price_tracker(chat_id, message_id, context):
    while True:
        try:
            price = await get_price()

            text = f"💰 BONK/USDT\n\nЦіна: {price}"

            await context.bot.edit_message_text(
                chat_id=chat_id,
                message_id=message_id,
                text=text,
            )

            await asyncio.sleep(5)

        except asyncio.CancelledError:
            break
        except Exception as e:
            print("Error:", e)
            await asyncio.sleep(5)


# --- /groshi ---
async def groshi(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id

    # якщо вже працює — не запускаємо другий раз
    if chat_id in active_tasks:
        await update.message.reply_text("⚠️ Вже запущено")
        return

    msg = await update.message.reply_text("⏳ Завантаження ціни...")

    task = asyncio.create_task(
        price_tracker(chat_id, msg.message_id, context)
    )

    active_tasks[chat_id] = task


# --- /stop ---
async def stop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id

    task = active_tasks.get(chat_id)

    if task:
        task.cancel()
        del active_tasks[chat_id]
        await update.message.reply_text("🛑 Оновлення зупинено")
    else:
        await update.message.reply_text("Нічого зупиняти 🙂")


# --- MAIN ---
def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("groshi", groshi))
    app.add_handler(CommandHandler("stop", stop))

    print("Bot started...")
    app.run_polling()


if __name__ == "__main__":
    main()