import subprocess
import re
from bot.config import KNOWN_WIFI

IW_INTERFACE = "wlan0"


def _run_iw_scan() -> str:
    try:
        result = subprocess.run(
            ["sudo", "iw", "dev", IW_INTERFACE, "scan"],
            capture_output=True,
            text=True,
            timeout=15,
        )
        return result.stdout
    except Exception:
        return ""


def scan_wifi():
    raw = _run_iw_scan()

    # Temporary storage: SSID -> best RSSI
    ssid_map: dict[str, float] = {}

    current_signal = None
    current_ssid = None

    for line in raw.splitlines():
        line = line.strip()

        # signal level
        if line.startswith("signal:"):
            match = re.search(r"signal:\s*(-?\d+\.\d+)", line)
            if match:
                current_signal = float(match.group(1))

        # SSID
        elif line.startswith("SSID:"):
            current_ssid = line.replace("SSID:", "").strip()

            if not current_ssid or current_signal is None:
                continue

            # keep strongest signal per SSID
            if (
                current_ssid not in ssid_map
                or current_signal > ssid_map[current_ssid]
            ):
                ssid_map[current_ssid] = current_signal

            current_signal = None
            current_ssid = None

    result = []

    for ssid, rssi in ssid_map.items():
        result.append({
            "ssid": ssid,
            "signal": _signal_to_percent(int(rssi)),
            "known": ssid in KNOWN_WIFI,
        })

    # Sort strongest first
    result.sort(key=lambda x: x["signal"], reverse=True)
    return result


def _signal_to_percent(rssi: int) -> int:
    if rssi <= -100:
        return 0
    if rssi >= -50:
        return 100
    return 2 * (rssi + 100)
