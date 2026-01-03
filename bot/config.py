import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN not set")

# -------------------------
# Known Wi-Fi networks
# SSID : PASSWORD
# -------------------------
KNOWN_WIFI = {
    "testtest": "test123456",
    "wls": "12345678"
}
