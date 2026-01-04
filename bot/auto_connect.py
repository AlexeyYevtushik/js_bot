# bot/auto_connect.py
from bot.wifi_manager import (
    scan_wifi,
    connect_wifi,
    has_internet,
    current_connected_ssid,
)
from bot.config import KNOWN_WIFI
from bot.notifier import notify


def main():
    notify("🚀 Auto Wi-Fi manager started")

    # 1️⃣ Check existing internet connection
    if has_internet():
        ssid = current_connected_ssid()
        ssid_text = ssid if ssid else "Unknown"
        notify(f"🌐 Internet connection exists. Connected Wi-Fi SSID: {ssid_text}")
        return

    notify("⚠️ No internet connection. Searching for known Wi-Fi networks…")

    # 2️⃣ Scan and filter known networks
    networks = scan_wifi()
    known_networks = [n for n in networks if n["known"]]

    if not known_networks:
        notify("❌ No known Wi-Fi networks found")
        return

    # 3️⃣ Try known networks by signal strength
    for net in known_networks:
        ssid = net["ssid"]
        password = KNOWN_WIFI.get(ssid)

        notify(f"🔌 Trying {ssid} ({net['signal']}%)")

        if not connect_wifi(ssid, password):
            notify(f"❌ Connection failed: {ssid}")
            continue

        if has_internet():
            notify(f"✅ Internet connection exists. Connected Wi-Fi SSID: {ssid}")
            return

        notify(f"⚠️ Connected to {ssid} but no internet access")

    # 4️⃣ All attempts failed
    notify("🚨 No internet connection is available")


if __name__ == "__main__":
    main()
