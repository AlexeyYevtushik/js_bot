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
