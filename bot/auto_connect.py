from bot.wifi_manager import (
    scan_wifi,
    connect_wifi,
    has_internet,
    current_connected_ssid,
)
from bot.config import KNOWN_WIFI
from bot.notifier import notify

pending_messages = []

def safe_notify(text: str):
    if has_internet():
        notify(text)
        for msg in pending_messages:
            notify(msg)
        pending_messages.clear()
    else:
        pending_messages.append(text)


def main():
    safe_notify("🚀 Auto Wi-Fi manager started")

    # 1️⃣ Already online?
    if has_internet():
        ssid = current_connected_ssid() or "Unknown"
        safe_notify(f"🌐 Internet connection exists. Connected Wi-Fi SSID: {ssid}")
        return

    safe_notify("⚠️ No internet connection. Searching for known Wi-Fi networks…")

    networks = scan_wifi()
    known_networks = [n for n in networks if n["known"]]

    if not known_networks:
        safe_notify("❌ All known Wi-Fi networks failed")
        return

    for net in known_networks:
        ssid = net["ssid"]
        password = KNOWN_WIFI.get(ssid)

        safe_notify(f"🔌 Connecting to SSID \"{ssid}\" ({net['signal']}%)")

        if not connect_wifi(ssid, password):
            safe_notify(f"❌ Connection failed: {ssid}")
            continue

        if has_internet():
            safe_notify(f"✅ Internet connection exists on SSID \"{ssid}\"")
            return

        safe_notify(f"⚠️ No internet connection on SSID \"{ssid}\"")

    safe_notify("🚨 All known Wi-Fi networks failed")


if __name__ == "__main__":
    main()
