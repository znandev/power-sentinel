import time
import requests
import state

from config import *
from database import (
    get_statistics,
    get_recent_events_text
)
from notification import telegram

offset = 0

def build_status():

    import time

    elapsed = int(
        time.time() - state.last_seen
    )

    return f"""
🟢 PowerSentinel Status

━━━━━━━━━━━━━

🖥 Server
{SERVER_HOSTNAME}

🌍 Server IP
{SERVER_IP}

⚡ Power
{state.power_state}

📡 ESP
{"ONLINE" if elapsed < ESP_TIMEOUT else "OFFLINE"}

📟 Model
{state.model}

🔖 Firmware
{state.firmware}

📶 ESP IP
{state.esp_ip}

🫀 Last Heartbeat
{elapsed}s ago

⏱ Countdown
{"RUNNING" if state.countdown_running else "IDLE"}

⏳ Remaining
{state.countdown}s
"""

def process_command(text):

    print(f"[BOT] Command: {text}")

    if text == "/ping":

        telegram("pong 🏓")

    elif text == "/status":

        telegram(
            build_status()
        )

    elif text == "/stats":

        stats = get_statistics()

        telegram(
    f"""
    📊 Statistics

    ━━━━━━━━━━━━━━━━━━

    ⚡ Power Lost Today
    {stats['power_lost_today']}

    ✅ Power Restored Today
    {stats['power_restored_today']}

    🛑 Shutdown Today
    {stats['shutdown_today']}

    ⏱ Countdown Today
    {stats['countdown_today']}

    📦 Total Events
    {stats['total_events']}
    """
        )

    elif text == "/events":

        telegram(

    f"""
    📜 Recent Events

    ━━━━━━━━━━━━━━━━━━

    {get_recent_events_text()}
    """

        )

    elif text == "/help":

        telegram(

    """
    📚 Available Commands

    /ping
    /status
    /stats
    /events
    /help
    /cancel
    """
        )
    
    elif text == "/cancel":

        if state.countdown_running:

            state.countdown_running = False
            state.countdown = 0

            telegram(
    """
    🛑 Shutdown Cancelled

    Countdown stopped via Telegram.
    """
            )

        else:

            telegram(
    """
    ℹ No active countdown.
    """
            )
    
    elif text == "/test":

        telegram(

    """
    ✅ Telegram Bot Working
    """
        )

def telegram_bot():

    global offset

    print("[BOT] Telegram Bot Started")

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

                offset = item["update_id"] + 1

                msg = item.get(
                    "message",
                    {}
                )

                text = msg.get(
                    "text",
                    ""
                )

                if str(msg.get("chat", {}).get("id")) != str(CHAT_ID):

                    continue

                process_command(
                    text.strip()
                )

        except Exception as e:

            import traceback

            print(f"[BOT ERROR] {e}")

            traceback.print_exc()

        time.sleep(
            TELEGRAM_POLLING_INTERVAL
        )