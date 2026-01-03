import asyncio
from telegram import Bot
from bot.config import BOT_TOKEN, CHAT_ID

async def send_test_message():
    bot = Bot(token=BOT_TOKEN)
    await bot.send_message(
        chat_id=CHAT_ID,
        text="✅ Raspberry Pi Wi-Fi Bot started successfully"
    )

if __name__ == "__main__":
    asyncio.run(send_test_message())
