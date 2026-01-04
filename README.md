# Raspberry Pi Telegram Wi-Fi Manager Bot

A Python-based Telegram bot for Raspberry Pi 4 that automatically manages Wi-Fi connections and allows manual control via Telegram.

---

## 🚀 Features

- Auto-start on Raspberry Pi boot
- Priority Wi-Fi connection logic
- Internet availability check
- Telegram-based Wi-Fi management
- Known / Unknown Wi-Fi handling
- Safe rollback on connection failure

---

## 🧠 Auto Connection Logic

1. On boot:
   - Verify internet access
2. If unavailable:
   - Scan all SSIDs
   - Sort by signal strength
   - Try connecting in priority order
3. After connection:
   - Verify internet access
4. On failure:
   - Try next Wi-Fi
5. If no Wi-Fi works:
   - Send error message to Telegram

---

## 📲 Telegram Commands

### `wifi` or `WI-FI`
Returns a list of available networks:

HomeWiFi - 85% - Known

OfficeNet - 72% - Unknown

yaml
Copy code

### Selecting Wi-Fi
- Send the number to connect
- If Unknown → bot asks for password
- On error → reconnects to previous Wi-Fi

---

## 🧰 Tech Stack

- Python 3.13
- python-telegram-bot 20.7
- iw / nmcli
- systemd
- Raspberry Pi OS

---

## 📂 Project Structure
```bash
js_bot/
	README.md
	requirements.txt

js_bot/
   bot/
	   config.py
   	auto_connect.py
   	bot.py
   	config.py
   	handlers.py
   	notifier.py
   	state_manager.py
   	wifi_manager.py
```

## Installation

```bash
TODO

```

## Running
python -m bot.bot

## Current code
```auto_connect.py
# bot/auto_connect.py
from bot.wifi_manager import scan_wifi, connect_wifi, has_internet
from bot.config import KNOWN_WIFI
from bot.notifier import notify


def main():
    notify("🚀 Auto Wi-Fi manager started")

    networks = scan_wifi()
    known_networks = [n for n in networks if n["known"]]

    if not known_networks:
        notify("❌ No known Wi-Fi networks found")
        return

    for net in known_networks:
        ssid = net["ssid"]
        password = KNOWN_WIFI[ssid]

        notify(f"🔌 Trying {ssid} ({net['signal']}%)")

        if not connect_wifi(ssid, password):
            notify(f"❌ Connection failed: {ssid}")
            continue

        if not has_internet():
            notify(f"⚠️ No internet on {ssid}")
            continue

        notify(f"✅ Connected to {ssid} with internet")
        return

    notify("🚨 All known Wi-Fi networks failed")


if __name__ == "__main__":
    main()
```

```bot.py
# bot/bot.py
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    filters,
)
from bot.config import BOT_TOKEN
from bot.handlers import start, handle_text
from bot.wifi_manager import scan_wifi, current_connected_ssid

# New handler for "Wi-Fi" messages
async def available_wifi(update, context):
    networks = scan_wifi()
    current_ssid = current_connected_ssid()

    # Deduplicate SSIDs and take strongest signal
    ssid_dict = {}
    for net in networks:
        ssid = net["ssid"]
        signal = net["signal"]
        known = net["known"]
        if ssid not in ssid_dict or signal > ssid_dict[ssid]["signal"]:
            ssid_dict[ssid] = {"signal": signal, "known": known}

    # Build message
    msg = "Available Wi-Fi networks:\n"
    for i, (ssid, info) in enumerate(sorted(ssid_dict.items(), key=lambda x: x[1]["signal"], reverse=True), start=1):
        status = "Known" if info["known"] else "Unknown"
        connected = " (Connected)" if ssid == current_ssid else ""
        msg += f"{i}. {ssid} ({info['signal']}%) [{status}]{connected}\n"

    await update.message.reply_text(msg)


def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    # This handles messages like "wifi" or "wi-fi" (case-insensitive)
    app.add_handler(MessageHandler(filters.Regex("(?i)^wi-?fi$"), available_wifi))
    # All other text messages go to your generic handler
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

    print("✅ Telegram Wi-Fi Bot running")
    app.run_polling()


if __name__ == "__main__":
    main()
```

```config.py
# bot/config.py
import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = int(os.getenv("CHAT_ID"))

if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN not set")

# Known Wi-Fi networks
KNOWN_WIFI = {
    "wls": "12345678",
    "testtest": "test123456",
}

INTERNET_CHECK_HOST = "8.8.8.8"
INTERNET_CHECK_TIMEOUT = 3
```

```handlers.py
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
```

```notifier.py
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
```

```wifi_manager.py
# bot/wifi_manager.py
import subprocess
import time
import re
from bot.config import KNOWN_WIFI, INTERNET_CHECK_HOST, INTERNET_CHECK_TIMEOUT

IW_INTERFACE = "wlan0"


def scan_wifi():
    try:
        result = subprocess.run(
            ["sudo", "iw", "dev", IW_INTERFACE, "scan"],
            capture_output=True,
            text=True,
            timeout=15,
        )
    except Exception:
        return []

    ssid_map = {}
    current_signal = None

    for line in result.stdout.splitlines():
        line = line.strip()

        if line.startswith("signal:"):
            m = re.search(r"signal:\s*(-?\d+\.\d+)", line)
            if m:
                current_signal = float(m.group(1))

        elif line.startswith("SSID:") and current_signal is not None:
            ssid = line.replace("SSID:", "").strip()
            if not ssid:
                continue

            if ssid not in ssid_map or current_signal > ssid_map[ssid]:
                ssid_map[ssid] = current_signal

            current_signal = None

    networks = []
    for ssid, rssi in ssid_map.items():
        networks.append({
            "ssid": ssid,
            "signal": _signal_to_percent(int(rssi)),
            "known": ssid in KNOWN_WIFI,
        })

    networks.sort(key=lambda x: x["signal"], reverse=True)
    return networks


def connect_wifi(ssid: str, password: str) -> bool:
    try:
        subprocess.run(
            ["nmcli", "connection", "delete", ssid],
            capture_output=True
        )

        cmd = ["nmcli", "dev", "wifi", "connect", ssid, "password", password]
        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode != 0:
            return False

        time.sleep(5)
        return True

    except Exception:
        return False


def has_internet() -> bool:
    try:
        result = subprocess.run(
            ["ping", "-c", "1", "-W", str(INTERNET_CHECK_TIMEOUT), INTERNET_CHECK_HOST],
            capture_output=True,
        )
        return result.returncode == 0
    except Exception:
        return False


def _signal_to_percent(rssi: int) -> int:
    if rssi <= -100:
        return 0
    if rssi >= -50:
        return 100
    return 2 * (rssi + 100)
```

```state_manager.py
# bot/state_manager.py
# Simple in-memory FSM per chat

_user_states = {}

def set_state(chat_id: int, action: str, data=None):
    _user_states[chat_id] = {
        "action": action,
        "data": data
    }

def get_state(chat_id: int):
    return _user_states.get(chat_id, {
        "action": None,
        "data": None
    })

def clear_state(chat_id: int):
    _user_states.pop(chat_id, None)
```

```requirements.txt
# requirements.txt
python-telegram-bot==20.7
python-dotenv==1.0.0
```