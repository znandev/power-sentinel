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

app = Flask(__name__)

# ======================================================
# GLOBAL
# ======================================================

power_state = "UNKNOWN"

countdown = 0
countdown_running = False

shutdown_thread = None

last_seen = time.time()

device_name = "UNKNOWN"
firmware = "UNKNOWN"
model = "UNKNOWN"

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

                event_shutdown(device_name)

                execute_shutdown()

                return

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

    state = request.args.get("state", "UNKNOWN").upper()

    if state not in ("ON", "OFF"):
        return "Invalid", 400
    
    device = request.args.get(
        "device",
        device_name
    )

    fw = request.args.get(
        "fw",
        firmware
    )

    device_model = request.args.get(
        "model",
        model
    )

    with LOCK:

        device_name = device
        firmware = fw
        model = device_model

        previous_state = power_state

        # =====================================
        # POWER LOST
        # =====================================

        if state == "OFF":

            if previous_state != "OFF":

                power_state = "OFF"

                log("Power Lost")

                event_power_lost(device_name)

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

        elif state == "ON":

            if previous_state != "ON":

                power_state = "ON"

                log("Power Restored")

                event_power_restored(device_name)

            if countdown_running:

                log("Countdown cancelled")

                event_countdown_cancelled(device_name)

                countdown_running = False

                countdown = 0

    return "OK"

@app.route("/heartbeat")
def heartbeat():

    global last_seen
    global power_state
    global device_name
    global firmware
    global model

    with LOCK:

        last_seen = time.time()

        power_state = request.args.get(
            "power",
            power_state
        ).upper()

        device_name = request.args.get(
            "device",
            device_name
        )

        firmware = request.args.get(
            "fw",
            firmware
        )

        model = request.args.get(
            "model",
            model
        )

    return jsonify({

        "status": "ok"

    })

@app.route("/status")
def status():

    with LOCK:

        esp_online = (
            time.time() - last_seen
        ) < ESP_TIMEOUT

        return jsonify({

            "power": power_state,
            "countdown": countdown,
            "running": countdown_running,
            "esp_online": esp_online,
            "device": device_name,
            "firmware": firmware,
            "model": model

        })

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

app.run(
    host=HOST,
    port=PORT,
    threaded=True
)