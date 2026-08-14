from flask import Flask, request, jsonify, render_template
from datetime import datetime
from database import (
    init_db, 
    insert_event,
    get_events,
    get_recent_events,
    get_last_event,
    get_statistics
)
from config import *
from notification import *
from telegram_bot import telegram_bot
from event import (
    event_power_lost,
    event_power_restored,
    event_countdown_started,
    event_countdown_cancelled,
    event_shutdown,
    event_heartbeat,
    event_esp_online,
    event_esp_offline
)

import threading
import subprocess
import time
import state

app = Flask(__name__)

# ======================================================
# GLOBAL
# ======================================================

shutdown_thread = None
startup_sent = False

LOCK = threading.Lock()

# ======================================================
# LOGGER
# ======================================================

def log(message):

    print(
        f"[{datetime.now().strftime('%H:%M:%S')}] {message}",
        flush=True
    )

# ======================================================
# SHUTDOWN
# ======================================================

def execute_shutdown():

    log("=" * 50)

    log("PowerSentinel Shutdown Sequence")

    log("=" * 50)

    if not SHUTDOWN_ENABLED:

        log("Shutdown disabled by configuration.")

        return

    if STOP_SERVICES:

        log("Stopping configured services...")

        for service in SERVICES:

            try:

                log(f"Stopping {service}")

                subprocess.run(

                    [

                        "systemctl",

                        "stop",

                        service

                    ],

                    timeout=SERVICE_TIMEOUT,

                    check=False

                )

            except Exception as e:

                log(f"{service} : {e}")

    log("Executing system shutdown...")

    subprocess.run(

        [

            "sudo",

            "shutdown",

            "-h",

            "now"

        ]

    )

def shutdown_timer():

    global countdown
    global countdown_running

    while True:

        time.sleep(1)

        with LOCK:

            if not countdown_running:

                return

            countdown -= 1

            if countdown < 0:
                countdown = 0

            log(f"Countdown : {countdown}s")

            if countdown == 0:

                countdown_running = False

                event_shutdown(
                    state.device_name
                )

                notify_shutdown(

                    state.model,
                    state.firmware,
                    state.esp_ip

                )

                execute_shutdown()

                return

# ========================
# NOTIFY HELPER
# ========================
def current_time():

    return datetime.now().strftime(

        "%Y-%m-%d %H:%M:%S"

    )

# ======================================================
# ROUTES
# ======================================================

@app.route("/")
def home():

    return render_template("index.html")


@app.route("/pln")
def pln():

    global power_state
    global countdown
    global countdown_running
    global shutdown_thread
    global device_name
    global firmware
    global model

    esp_ip = request.remote_addr

    pln_state = request.args.get(
        "state",
        "UNKNOWN"
    ).upper()

    if pln_state not in ("ON", "OFF"):
        return "Invalid", 400
    
    device = request.args.get(
        "device",
        state.device_name
    )

    fw = request.args.get(
        "fw",
        state.firmware
    )

    device_model = request.args.get(
        "model",
        state.model
    )

    with LOCK:

        device_name = device
        firmware = fw
        model = device_model

        previous_state = power_state

        # =====================================
        # POWER LOST
        # =====================================

        if pln_state == "OFF":

            if previous_state != "OFF":

                power_state = "OFF"

                log("Power Lost")

                event_power_lost(
                    state.device_name
                )

                notify_power_lost(

                    state.model,
                    state.firmware,
                    state.esp_ip,
                    state.power_state,
                    countdown

                )

            if not countdown_running:

                countdown = COUNTDOWN

                countdown_running = True

                log("Shutdown countdown started")

                event_countdown_started(device_name)

                shutdown_thread = threading.Thread(
                    target=shutdown_timer,
                    daemon=True
                )

                shutdown_thread.start()

        # =====================================
        # POWER RESTORED
        # =====================================

        elif pln_state == "ON":

            if previous_state != "ON":

                power_state = "ON"

                log("Power Restored")

                event_power_restored(
                    state.device_name
                )

                notify_power_restored(

                    state.model,
                    state.firmware,
                    state.esp_ip,
                    state.power_state
                )

            if countdown_running:

                log("Countdown cancelled")

                event_countdown_cancelled(device_name)

                countdown_running = False

                countdown = 0

    return "OK"

@app.route("/heartbeat")
def heartbeat():

    global startup_sent

    state.esp_seen_once = True

    import sys

    print(
        "[HEARTBEAT MODULE]",
        id(sys.modules[__name__])
    )

    with LOCK:

        state.last_seen = time.time()
        state.esp_seen_once = True

        state.power_state = request.args.get(
            "power",
            state.power_state
        ).upper()

        state.device_name = request.args.get(
            "device",
            state.device_name
        )

        state.firmware = request.args.get(
            "fw",
            state.firmware
        )

        state.model = request.args.get(
            "model",
            state.model
        )

        state.esp_ip = request.remote_addr

        if not startup_sent:

            startup_sent = True

            notify_startup(

                state.model,
                state.firmware,
                state.esp_ip,
                state.power_state

            )

    return jsonify({

        "status": "ok"

    })

@app.route("/status")
def status():

    with LOCK:

        esp_online = (
            time.time() - state.last_seen
        ) < ESP_TIMEOUT

        return jsonify({

            "power": state.power_state,
            "countdown": countdown,
            "running": countdown_running,
            "esp_online": esp_online,
            "device": state.device_name,
            "firmware": state.firmware,
            "model": state.model

        })

def esp_monitor():

    offline = False

    while True:

        time.sleep(1)

        if not state.esp_seen_once:
            continue

        elapsed = time.time()-state.last_seen

        print(
            f"[ESP_MON] elapsed={elapsed:.1f}"
        )

        if elapsed > ESP_TIMEOUT:

            if not offline:

                offline=True

                log("ESP Offline")

                event_esp_offline(
                    state.device_name
                )

                notify_esp_offline(

                    state.model,
                    state.firmware,
                    state.esp_ip

                )

                print("[ESP] OFFLINE TRIGGERED")

        else:

            if offline:

                offline=False

                with LOCK:

                    elapsed=time.time()-state.last_seen

                log("ESP Online")

                event_esp_online(
                    state.device_name
                )

                notify_esp_online(

                    state.model,
                    state.firmware,
                    state.esp_ip

                )

                print(
                    f"[ESP] elapsed={elapsed:.1f}s "
                    f"timeout={ESP_TIMEOUT} "
                    f"offline={offline}"
                )


@app.route("/events")
def events():

    return jsonify(
        get_recent_events()

    )

@app.route("/statistics")
def statistics():

    return jsonify(
        get_statistics()
    )

# ======================================================
# STARTUP
# ======================================================

init_db()

log("=" * 40)
log(f"{TITLE} Started")
log("Shutdown Configuration")
log("=" * 40)
log(f"Enabled        : {SHUTDOWN_ENABLED}")
log(f"Countdown      : {COUNTDOWN}")
log(f"Stop Services  : {STOP_SERVICES}")
log(f"Services       : {SERVICES}")
log(f"Listening on {HOST}:{PORT}")
log("=" * 40)

threading.Thread(
    target=esp_monitor,
    daemon=True
).start()

threading.Thread(
    target=telegram_bot,
    daemon=True
).start()

app.run(
    host=HOST,
    port=PORT,
    threaded=True
)