# bot/handlers.py
from telegram import Update
from telegram.ext import ContextTypes

from bot.state_manager import set_state, get_state, clear_state
from bot import wifi_manager


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    clear_state(chat_id)

    await context.bot.send_message(
        chat_id=chat_id,
        text=(
            "👋 Raspberry Pi Wi-Fi Bot is online.\n\n"
            "Send:\n"
            "• wifi"
        )
    )


async def available_wifi(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id

    wifi_list = wifi_manager.scan_wifi()

    msg = "📡 wifi networks:\n"
    for i, w in enumerate(wifi_list, start=1):
        known = "Known" if w["known"] else "Unknown"
        msg += f"{i}) {w['ssid']} — {w['signal']}% — {known}\n"

    await context.bot.send_message(chat_id=chat_id, text=msg)
    set_state(chat_id, "WAIT_WIFI_SELECTION", wifi_list)


async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    text = update.message.text.strip()
    state = get_state(chat_id)

    # ---- SELECT WIFI ----
    if state["action"] == "WAIT_WIFI_SELECTION":
        if not text.isdigit():
            await context.bot.send_message(chat_id, "❌ Send a number.")
            return

        idx = int(text) - 1
        wifi_list = state["data"]

        if idx < 0 or idx >= len(wifi_list):
            await context.bot.send_message(chat_id, "❌ Invalid selection.")
            return

        selected = wifi_list[idx]

        if selected["known"]:
            await context.bot.send_message(
                chat_id,
                f"🔌 Connecting to {selected['ssid']} (known network)…"
            )
            wifi_manager.connect_wifi(selected["ssid"])
            clear_state(chat_id)
        else:
            await context.bot.send_message(
                chat_id,
                f"🔑 Enter password for {selected['ssid']}:"
            )
            set_state(chat_id, "WAIT_WIFI_PASSWORD", selected)

    # ---- PASSWORD ----
    elif state["action"] == "WAIT_WIFI_PASSWORD":
        wifi = state["data"]
        password = text

        await context.bot.send_message(
            chat_id,
            f"🔌 Connecting to {wifi['ssid']}…"
        )

        wifi_manager.connect_wifi(wifi["ssid"], password)
        clear_state(chat_id)

    # ---- UNKNOWN ----
    else:
        await context.bot.send_message(
            chat_id,
            "❓ Unknown command. Send 'wifi'."
        )
