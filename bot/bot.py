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
