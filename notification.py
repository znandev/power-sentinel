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
🟢 <b>POWERSENTINEL STARTED</b>

══════════════════

<pre>
🖥 Server   : zn4ndserver
🌐 IP       : 10.77.227.100

⚡ Power    : 🟢 ON

📡 Model    : ESP8266-D1Mini
🏷 Firmware : 0.2.0
📶 ESP IP   : 10.42.74.5
</pre>

🕒 <i>2026-08-14 00:31:03</i>
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
🚨 <b>POWER FAILURE DETECTED</b>

══════════════════

<pre>
🖥 Server   : zn4ndserver

⚡ Power    : 🔴 OFF
⏳ Timer    : 20s

📡 Model    : ESP8266-D1Mini
🏷 Firmware : 0.2.0
📶 ESP IP   : 10.42.74.5
</pre>

⚠️ <b>Shutdown countdown started</b>

🕒 <i>2026-08-14 00:03:18</i>
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

══════════════════

<pre>
🖥 Server   : zn4ndserver

⚡ Power    : 🟢 ON
🛑 Timer    : CANCELLED

📡 Model    : ESP8266-D1Mini
🏷 Firmware : 0.2.0
📶 ESP IP   : 10.42.74.5
</pre>

🔋 <b>Utility power recovered</b>

🕒 <i>2026-08-14 00:03:51</i>
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

══════════════════

<pre>
🖥 Server   : zn4ndserver

⚡ Power    : OFF
📡 Model    : ESP8266-D1Mini
🏷 Firmware : 0.2.0
📶 ESP IP   : 10.42.74.5
</pre>

☠️ <b>Executing shutdown sequence</b>

🕒 <i>2026-08-14 00:03:38</i>
"""
    )

def notify_esp_offline(

    esp_model,
    esp_fw,
    esp_ip

):

    telegram(

f"""
🔴 <b>ESP OFFLINE</b>

══════════════════

<pre>
🖥 Server   : zn4ndserver

📡 Model    : ESP8266-D1Mini
🏷 Firmware : 0.2.0
📶 ESP IP   : 10.42.74.5

💔 Status   : NO HEARTBEAT
</pre>

⚠️ <b>Device communication lost</b>

🕒 <i>2026-08-14 00:05:22</i>
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

══════════════════

<pre>
🖥 Server   : zn4ndserver

📡 Model    : ESP8266-D1Mini
🏷 Firmware : 0.2.0
📶 ESP IP   : 10.42.74.5

💚 Status   : CONNECTED
</pre>

📶 <b>Heartbeat restored</b>

🕒 <i>2026-08-14 00:05:31</i>
"""
    )