# bot/notifier.py
import asyncio
from telegram import Bot
from bot.config import BOT_TOKEN, CHAT_ID


async def _send(text: str):
    bot = Bot(token=BOT_TOKEN)
    await bot.send_message(chat_id=CHAT_ID, text=text)


def notify(text: str):
    try:
        asyncio.run(_send(text))
    except RuntimeError:
        # event loop already running (safe fallback)
        loop = asyncio.get_event_loop()
        loop.create_task(_send(text))
