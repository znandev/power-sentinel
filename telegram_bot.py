import time
import requests
import state

from config import *
from database import (
    get_statistics,
    get_recent_events_text
)

from notification import (
    telegram,
    telegram_api
)

offset = 0


# ======================================================
# STATUS VIEW
# ======================================================
def format_uptime(seconds):

    days = seconds // 86400
    hours = (seconds % 86400) // 3600
    minutes = (seconds % 3600) // 60

    if days > 0:
        return f"{days}d {hours}h {minutes}m"

    if hours > 0:
        return f"{hours}h {minutes}m"

    return f"{minutes}m"

def wifi_quality(rssi):

    if rssi >= -60:
        return "🟢 Excellent"

    elif rssi >= -70:
        return "🟡 Good"

    elif rssi >= -80:
        return "🟠 Fair"

    return "🔴 Poor"

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

def build_status():

    elapsed = int(
        time.time() - state.last_seen
    )

    esp_online = (
        elapsed < ESP_TIMEOUT
    )

    utility = (
        "🟢 ON"
        if state.power_state == "ON"
        else "🔴 OFF"
    )

    esp = (
        "🟢 ONLINE"
        if esp_online
        else "🔴 OFFLINE"
    )

    timer = (
        f"⏳ {state.countdown}s"
        if state.countdown_running
        else "✅ IDLE"
    )

    return f"""
🖥 <b>POWERSENTINEL STATUS</b>
────────────────────
🖥 <b>Server</b>: {SERVER_HOSTNAME} 
🌐 <b>IP</b>: {SERVER_IP}      
⚡ <b>Utility</b>: {utility}
📡 <b>ESP Status</b>: {esp}
📟 <b>Model</b>: {state.model}
🏷 <b>Firmware</b>: {state.firmware}
📶 <b>ESP IP</b>: {state.esp_ip}
📡 <b>WiFi</b>: {state.ssid}
📶 <b>Signal</b>: {signal_bar(state.rssi)}
📊 <b>RSSI</b>: {state.rssi} dBm
🎯 <b>Quality</b>: {wifi_quality(state.rssi)}
🧠 <b>Heap</b>: {state.heap:,} bytes
⏱ <b>Uptime</b>: {format_uptime(state.uptime)}
🫀 <b>Last HB</b>: {elapsed}s
⏳ <b>Timer</b>: {timer}

🕒 <i>{time.strftime("%Y-%m-%d %H:%M:%S")}</i>
<i>Developed by @nandzie</i>
"""

# ======================================================
# CALLBACK BUTTONS
# ======================================================

def process_callback(action):

    print(
        f"[BOT] Callback: {action}"
    )

    if action == "status":

        telegram(
            build_status()
        )

    elif action == "events":

        telegram(

f"""
📜 <b>RECENT EVENTS</b>
──────────────────
<pre>
{get_recent_events_text()}
</pre>

🕒 <i>{time.strftime("%Y-%m-%d %H:%M:%S")}</i>
<i>Developed by @nandzie</i>
""",

        keyboard=True

    )

    elif action == "cancel":

        if state.countdown_running:

            state.countdown_running = False
            state.countdown = 0

            telegram(

"""
🛑 <b>SHUTDOWN CANCELLED</b>

✅ Countdown stopped
via Telegram control panel.
"""
            )

        else:

            telegram(

"""
ℹ️ <b>NO ACTIVE COUNTDOWN</b>

Nothing to cancel.
"""
            )

    elif action == "refresh":

        telegram(
            build_status()
        )


# ======================================================
# COMMANDS
# ======================================================

def process_command(text):

    print(
        f"[BOT] Command: {text}"
    )

    if text == "/ping":

        telegram(
            "pong 🏓"
        )

    elif text == "/status":

        telegram(
            build_status()
        )

    elif text == "/stats":

        stats = get_statistics()

        telegram(

f"""
📊 <b>SYSTEM STATISTICS</b>
────────────────
⚡ <b>Power Lost</b>:{stats['power_lost_today']}
✅ <b>Power Restored</b>: {stats['power_restored_today']}
🛑 <b>Shutdown Executed</b>: {stats['shutdown_today']}
⏳ <b>Countdown Started</b>: {stats['countdown_today']}
📦 <b>Total Events</b>: {stats['total_events']}

🕒 <i>{time.strftime("%Y-%m-%d %H:%M:%S")}</i>
<i>Developed by @nandzie</i>
""",

        keyboard=True

    )

    elif text == "/events":

        telegram(

f"""
📜 <b>RECENT EVENTS</b>
──────────────────
<pre>
{get_recent_events_text()}
</pre>

🕒 <i>{time.strftime("%Y-%m-%d %H:%M:%S")}</i>
<i>Developed by @nandzie</i>
""",
        keyboard=True
        
    )

    elif text == "/cancel":

        if state.countdown_running:

            state.countdown_running = False
            state.countdown = 0

            telegram(

f"""
🛑 <b>SHUTDOWN CANCELLED</b>
──────────────────

✅ Automatic shutdown disarmed.

⚡ Utility monitoring
continues normally.

🕒 <i>{time.strftime("%Y-%m-%d %H:%M:%S")}</i>
<i>Developed by @nandzie</i>
"""
            )

        else:

            telegram(

"""
ℹ️ <b>NO ACTIVE COUNTDOWN</b>

Nothing to cancel.
"""
            )

    elif text == "/help":

        telegram(

"""
📚 <b>AVAILABLE COMMANDS</b>
──────────────────
📊 /status
System status
📈 /stats
Statistics
📜 /events
Recent events
🛑 /cancel
Cancel shutdown
🏓 /ping
Connectivity test
🧪 /test
Telegram test
"""
        )

    elif text == "/test":

        telegram(

"""
✅ <b>TELEGRAM BOT WORKING</b>
"""
        )


# ======================================================
# BOT LOOP
# ======================================================

def telegram_bot():

    global offset

    print(
        "[BOT] Telegram Bot Started"
    )

    while True:

        try:

            r = requests.get(

                f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates",

                params={

                    "offset": offset,
                    "timeout": 20

                },

                timeout=30

            ).json()

            for item in r.get(
                "result",
                []
            ):

                offset = (
                    item["update_id"] + 1
                )

                # =====================================
                # CALLBACK BUTTON
                # =====================================

                callback = item.get(
                    "callback_query"
                )

                if callback:

                    chat_id = callback[
                        "message"
                    ]["chat"]["id"]

                    if str(chat_id) != str(CHAT_ID):

                        continue

                    process_callback(
                        callback["data"]
                    )

                    telegram_api(

                        "answerCallbackQuery",

                        {

                            "callback_query_id":
                            callback["id"]

                        }

                    )

                    continue

                # =====================================
                # NORMAL MESSAGE
                # =====================================

                msg = item.get(
                    "message",
                    {}
                )

                if not msg:

                    continue

                if str(

                    msg.get(
                        "chat",
                        {}
                    ).get("id")

                ) != str(CHAT_ID):

                    continue

                text = msg.get(
                    "text",
                    ""
                ).strip()

                if text:

                    process_command(
                        text
                    )

        except Exception as e:

            import traceback

            print(
                f"[BOT ERROR] {e}"
            )

            traceback.print_exc()

        time.sleep(
            TELEGRAM_POLLING_INTERVAL
        )