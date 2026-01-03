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
   - Check for SSID `testtest`
   - Connect using password `test123456`
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

### `wifi`
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

- Python 3.9+
- python-telegram-bot
- iw / nmcli
- systemd
- Raspberry Pi OS

---

## 📂 Project Structure
```bash
js_bot/
├── bot/
│   ├── __init__.py
│   ├── bot.py
│   └── config.py
├── logs/
├── .env
├── .gitignore
├── requirements.txt
└── README.md
```

yaml
Copy code

---

## ⚙️ Installation

```bash
sudo apt install iw network-manager
pip install -r requirements.txt
🔐 Environment Variables
Create .env:

ini
Copy code
BOT_TOKEN=your_bot_token
CHAT_ID=your_chat_id
🧩 Systemd Service
bash
Copy code
sudo cp service/wifi-bot.service /etc/systemd/system/
sudo systemctl enable wifi-bot
sudo systemctl start wifi-bot
📡 Internet Check
Ping 8.8.8.8

HTTPS request fallback

🛑 Error Handling
Automatic fallback to previous Wi-Fi

Telegram alerts on failures

Logs stored locally

📜 License
MIT

markdown
Copy code

---

If you want, next I can:
- Provide **full Python implementation**
- Generate **systemd service file**
- Create **Wi-Fi scanning & parsing code**
- Build **state machine diagram**
- Prepare **ready-to-push GitHub repo**

Just tell me what you want next.
