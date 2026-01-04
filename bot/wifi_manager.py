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
