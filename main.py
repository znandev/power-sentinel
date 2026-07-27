from flask import Flask, request, jsonify, render_template
from datetime import datetime
from config import *
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

    if TEST_MODE:

        log("=" * 40)
        log("TEST MODE")
        log("EXECUTE SHUTDOWN")
        log("=" * 40)

        subprocess.run([
            "touch",
            "/tmp/ups_guardian_shutdown_test"
        ])

        log("Created /tmp/ups_guardian_shutdown_test")

    else:

        log("Executing system shutdown...")

        subprocess.run([
            "sudo",
            "shutdown",
            "-h",
            "now"
        ])


def shutdown_timer():

    global countdown
    global countdown_running

    while True:

        time.sleep(1)

        with LOCK:

            if not countdown_running:

                log("Countdown cancelled")
                return

            countdown -= 1

            if countdown < 0:
                countdown = 0

            log(f"Countdown : {countdown}s")

            if countdown == 0:

                countdown_running = False

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

    state = request.args.get("state", "UNKNOWN").upper()

    if state not in ("ON", "OFF"):
        return "Invalid", 400

    with LOCK:

        power_state = state

        if state == "OFF":

            if not countdown_running:

                log("Power Lost")

                countdown = COUNTDOWN
                countdown_running = True

                shutdown_thread = threading.Thread(
                    target=shutdown_timer,
                    daemon=True
                )

                shutdown_thread.start()

        else:

            if countdown_running:
                log("Power Restored")

            countdown_running = False
            countdown = 0

    return "OK"


@app.route("/heartbeat")
def heartbeat():

    global last_seen
    global power_state
    global device_name
    global firmware

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
            "firmware": firmware

        })

# ======================================================
# STARTUP
# ======================================================

log("=" * 40)
log(f"{TITLE} Started")
log(f"Listening on {HOST}:{PORT}")
log("=" * 40)

app.run(
    host=HOST,
    port=PORT,
    threaded=True
)