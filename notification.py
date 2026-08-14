import requests
from datetime import datetime

from config import *

# ======================================================
# TELEGRAM
# ======================================================

import requests
from requests.exceptions import RequestException

def telegram(message):

    if not NOTIFICATION_ENABLED:
        return

    if not TELEGRAM_ENABLED:
        return

    try:

        response = requests.post(

            f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",

            data={

                "chat_id": CHAT_ID,

                "text": message,

                "parse_mode": "HTML"

            },

            timeout=10

        )

        print(response.text)

        response.raise_for_status()

    except Exception as e:

        print(e)

        print(f"[Telegram] Failed : {e}")

def telegram_api(method, data=None):

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/{method}"

    try:

        r = requests.post(
            url,
            data=data,
            timeout=15
        )

        return r.json()

    except Exception as e:

        print(f"[Telegram] {e}")

        return {}

def now():

    return datetime.now().strftime(

        "%Y-%m-%d %H:%M:%S"

    )

def notify_startup(

    esp_model,
    esp_fw,
    esp_ip,
    power

):

    telegram(

f"""
🟢 <b>PowerSentinel Started</b>

━━━━━━━━━━━━━━━━━━

🖥 <b>Server</b>
{SERVER_HOSTNAME}

🌐 <b>Server IP</b>
{SERVER_IP}

📡 <b>ESP Model</b>
{esp_model}

🔖 <b>Firmware</b>
{esp_fw}

📶 <b>ESP IP</b>
{esp_ip}

⚡ <b>Power</b>
{power}

🕒 <b>Time</b>
{now()}
"""
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
🚨 <b>POWER LOST</b>

━━━━━━━━━━━━━━━━━━

🖥 <b>Server</b>
{SERVER_HOSTNAME}

🌐 <b>Server IP</b>
{SERVER_IP}

📡 <b>ESP Model</b>
{esp_model}

🔖 <b>Firmware</b>
{esp_fw}

📶 <b>ESP IP</b>
{esp_ip}

⚡ <b>Power</b>
{power}

⏳ <b>Shutdown</b>
{countdown} Seconds

🕒 <b>Time</b>
{now()}
"""
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

━━━━━━━━━━━━━━━━━━

🖥 <b>Server</b>
{SERVER_HOSTNAME}

🌐 <b>Server IP</b>
{SERVER_IP}

📡 <b>ESP Model</b>
{esp_model}

🔖 <b>Firmware</b>
{esp_fw}

📶 <b>ESP IP</b>
{esp_ip}

⚡ <b>Power</b>
{power}

🛑 <b>Countdown</b>
Cancelled

🕒 <b>Time</b>
{now()}
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

━━━━━━━━━━━━━━━━━━

🖥 <b>Server</b>
{SERVER_HOSTNAME}

🌐 <b>Server IP</b>
{SERVER_IP}

📡 <b>ESP Model</b>
{esp_model}

🔖 <b>Firmware</b>
{esp_fw}

📶 <b>ESP IP</b>
{esp_ip}

🕒 <b>Time</b>
{now()}
"""
    )

def notify_esp_offline(

    esp_model,
    esp_fw,
    esp_ip

):

    telegram(

f"""
⚠ <b>ESP OFFLINE</b>

━━━━━━━━━━━━━━━━━━

🖥 <b>Server</b>
{SERVER_HOSTNAME}

🌐 <b>Server IP</b>
{SERVER_IP}

📡 <b>ESP Model</b>
{esp_model}

🔖 <b>Firmware</b>
{esp_fw}

📶 <b>ESP IP</b>
{esp_ip}

💔 <b>Heartbeat Timeout</b>

🕒 <b>Time</b>
{now()}
"""
    )

def notify_esp_online(

    esp_model,
    esp_fw,
    esp_ip

):

    telegram(

f"""
🟢 <b>ESP ONLINE</b>

━━━━━━━━━━━━━━━━━━

🖥 <b>Server</b>
{SERVER_HOSTNAME}

🌐 <b>Server IP</b>
{SERVER_IP}

📡 <b>ESP Model</b>
{esp_model}

🔖 <b>Firmware</b>
{esp_fw}

📶 <b>ESP IP</b>
{esp_ip}

🕒 <b>Time</b>
{now()}
"""
    )