def scan_wifi():
    """
    Placeholder for real Wi-Fi scan (Milestone 3)
    """
    return [
        {"ssid": "testtest", "signal": 90, "known": True},
        {"ssid": "HomeNet", "signal": 74, "known": False},
        {"ssid": "CafeWiFi", "signal": 51, "known": True},
    ]

def connect_wifi(ssid: str, password: str | None = None) -> bool:
    """
    Placeholder for real Wi-Fi connect (Milestone 3)
    """
    return True
