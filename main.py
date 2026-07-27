from flask import Flask, request, jsonify, render_template
from datetime import datetime
import threading
import subprocess
import time

app = Flask(__name__)

# ===========================================
# CONFIG
# ===========================================

COUNTDOWN_SECONDS = 15      # nanti ganti 60
TEST_MODE = True            # nanti False

# ===========================================
# GLOBAL
# ===========================================

power_state = "UNKNOWN"

countdown = 0
countdown_running = False

shutdown_thread = None

LOCK = threading.Lock()

last_seen = time.time()

ESP_TIMEOUT = 15
# ===========================================
# LOGGER
# ===========================================

def log(message):

    print(
        f"[{datetime.now().strftime('%H:%M:%S')}] {message}",
        flush=True
    )

# ===========================================
# SHUTDOWN
# ===========================================

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

# ===========================================
# WEB
# ===========================================

@app.route("/")
def home():

    return render_template(
        "index.html",
        state=power_state,
        countdown=countdown,
        running=countdown_running
    )

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

                countdown = COUNTDOWN_SECONDS
                countdown_running = True

                shutdown_thread = threading.Thread(
                    target=shutdown_timer,
                    daemon=True
                )

                shutdown_thread.start()

        elif state == "ON":

            if countdown_running:

                log("Power Restored")

            countdown_running = False
            countdown = 0

    return "OK"

@app.route("/status")
def status():

    esp_online = (time.time() - last_seen) < ESP_TIMEOUT

    return jsonify({

        "power": power_state,
        "countdown": countdown,
        "running": countdown_running,
        "esp_online": esp_online

    })

@app.route("/heartbeat")
def heartbeat():

    global last_seen

    last_seen = time.time()

    return "OK"
# ===========================================
# START
# ===========================================

log("ESP UPS Guardian Started")

app.run(
    host="0.0.0.0",
    port=8080,
    threaded=True
)