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
