import json
import requests
import state

from datetime import datetime
from config import *

# ======================================================
# INLINE MENU
# ======================================================

def notification_menu():

    return {

        "inline_keyboard": [

            [
                {
                    "text": "📊 Status",
                    "callback_data": "status"
                },
                {
                    "text": "📜 Events",
                    "callback_data": "events"
                }
            ],

            [
                {
                    "text": "🛑 Cancel",
                    "callback_data": "cancel"
                },
                {
                    "text": "🔄 Refresh",
                    "callback_data": "refresh"
                }
            ]

        ]
    }

# ======================================================
# HELPERS
# ======================================================

def now():

    return datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )

def signal_bar(rssi):

    if rssi >= -60:
        return "▰▰▰▰▰"

    elif rssi >= -70:
        return "▰▰▰▰▱"

    elif rssi >= -80:
        return "▰▰▰▱▱"

    elif rssi >= -90:
        return "▰▰▱▱▱"

    return "▰▱▱▱▱"

# ======================================================
# TELEGRAM
# ======================================================

def telegram(

    message,
    keyboard=False

):

    if not NOTIFICATION_ENABLED:
        return

    if not TELEGRAM_ENABLED:
        return

    try:

        payload = {

            "chat_id": CHAT_ID,
            "text": message,
            "parse_mode": "HTML"

        }

        if keyboard:

            payload["reply_markup"] = json.dumps(
                notification_menu()
            )

        response = requests.post(

            f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",

            data=payload,

            timeout=10

        )

        print(response.text)

        response.raise_for_status()

    except Exception as e:

        print(
            f"[Telegram] Failed : {e}"
        )

# ======================================================
# RAW API
# ======================================================

def telegram_api(

    method,
    data=None

):

    url = (
        f"https://api.telegram.org/"
        f"bot{BOT_TOKEN}/{method}"
    )

    try:

        r = requests.post(

            url,
            data=data,
            timeout=15

        )

        return r.json()

    except Exception as e:

        print(
            f"[Telegram] {e}"
        )

        return {}

# ======================================================
# NOTIFICATIONS
# ======================================================

def notify_startup(

    esp_model,
    esp_fw,
    esp_ip,
    power

):

    telegram(

f"""
🟢 <b>POWERSENTINEL STARTED</b>
──────────────────
🖥 <b>Server</b>: {SERVER_HOSTNAME}
🌐 <b>IP</b>: {SERVER_IP}
📡 <b>Device</b>: {state.device_name}
🏷 <b>Firmware</b>: {esp_fw}
📶 <b>WiFi</b>: {state.ssid}
📡 <b>Signal</b>: {signal_bar(state.rssi)} ({state.rssi} dBm)
⚡ <b>Utility</b>: {"🟢 ON" if power == "ON" else "🔴 OFF"}

🚀 <b>Monitoring service ready</b>

🕒 <i>{now()}</i>
<i>Developed by @nandzie </i>
""",

        keyboard=True
    )

def notify_power_lost(

    esp_model,
    esp_fw,
    esp_ip,
    power,
    countdown

):

    telegram(
f"""
🚨 <b>POWER FAILURE DETECTED</b>
───────────────────
🖥 <b>Server</b>: {SERVER_HOSTNAME}
🌐 <b>IP</b>: {SERVER_IP}
⚡ <b>Utility</b>: 🔴 OFF
📡 <b>ESP Status</b>: 🟢 ONLINE
📶 <b>ESP Signal</b>: {signal_bar(state.rssi)} ({state.rssi} dBm)

⏳ <b>Shutdown</b>: {countdown}s

⚠️ <b>Automatic shutdown countdown started</b>

🕒 <i>{now()}</i>
""",

        keyboard=True

    )

def notify_power_restored(

    esp_model,
    esp_fw,
    esp_ip,
    power

):

    telegram(

f"""
✅ <b>POWER RESTORED</b>
───────────────────
🖥 <b>Server</b>: {SERVER_HOSTNAME}
🌐 <b>IP</b>: {SERVER_IP}
⚡ <b>Utility</b>: 🟢 ON
📡 <b>ESP</b>: 🟢 ONLINE
📶 <b>Signal</b>: {signal_bar(state.rssi)} ({state.rssi} dBm)
</pre>

🔋 <b>Utility power recovered</b>
🛑 <b>Shutdown cancelled</b>

🕒 <i>{now()}</i>
"""
    )

def notify_shutdown(

    esp_model,
    esp_fw,
    esp_ip

):

    telegram(

f"""
🛑 <b>SYSTEM SHUTDOWN</b>
───────────────────
🖥 <b>Server</b>: {SERVER_HOSTNAME}
⚡ <b>Utility</b>: 🔴 OFF
📡 <b>ESP Status</b>: 🟢 ONLINE
📶 <b>Signal</b>: {signal_bar(state.rssi)} ({state.rssi} dBm)

☠️ <b>Executing shutdown sequence</b>

🕒 <i>{now()}</i>
""",

        keyboard=True

    )

def notify_esp_offline(

    esp_model,
    esp_fw,
    esp_ip

):

    telegram(

f"""
🔴 <b>ESP OFFLINE</b>
───────────────────
🖥 <b>Server</b>: {SERVER_HOSTNAME}
📡 <b>Device</b>: {state.device_name}
📶 <b>Last RSSI</b>: {state.rssi} dBm

💔 <b>Heartbeat timeout detected</b>

⚠️ Communication with ESP lost

🕒 <i>{now()}</i>
""",

        keyboard=True

    )

def notify_esp_online(

    esp_model,
    esp_fw,
    esp_ip

):

    telegram(

f"""
🟢 <b>ESP ONLINE</b>
───────────────────
🖥 <b>Server</b>: {SERVER_HOSTNAME}
📡 <b>Device</b>: {state.device_name}
📶 <b>Signal</b>: {signal_bar(state.rssi)} ({state.rssi} dBm)
📡 <b>WiFi</b>: {state.ssid}

💚 <b>Communication restored</b>

🕒 <i>{now()}</i>
"""
    )