import asyncio
import aiohttp
from aiogram import Bot, Dispatcher
from aiogram.types import Message
from aiogram.filters import Command

TOKEN = "7830152931:AAGe1xmx1BW_q9eIld3mDlg0eOBiziKmPmY"

bot = Bot(token=TOKEN)
dp = Dispatcher()

tasks = {}


# ---------------- BINANCE PRICE ----------------
async def get_price():
    url = "https://api.binance.com/api/v3/ticker/price?symbol=BONKUSDT"

    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            data = await resp.json()
            return float(data["price"])


# ---------------- START ----------------
@dp.message(Command("start"))
async def start(message: Message):
    await message.answer("✅ Бот працює\n\n/groshi — ціна BONK")


# ---------------- LOOP ----------------
async def price_loop(chat_id: int):

    last_text = ""

    while True:
        try:
            price = await get_price()
            text = f"💰 BONK/USDT: {price:.8f}"

            if text != last_text:
                await bot.send_message(chat_id, text)
                last_text = text

        except Exception as e:
            print("ERROR:", e)

        await asyncio.sleep(10)


# ---------------- COMMAND ----------------
@dp.message(Command("groshi"))
async def groshi(message: Message):

    chat_id = message.chat.id

    if chat_id in tasks:
        await message.answer("⚠️ Уже запущено")
        return

    task = asyncio.create_task(price_loop(chat_id))
    tasks[chat_id] = task

    await message.answer("📈 Відправляю ціну...")


# ---------------- MAIN ----------------
async def main():
    print("BOT STARTED ✅")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())