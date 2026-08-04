from datetime import datetime
from database import insert_event

# ======================================================
# SEVERITY
# ======================================================

INFO = "INFO"
WARNING = "WARNING"
ERROR = "ERROR"
CRITICAL = "CRITICAL"

# ======================================================
# EVENT TYPE
# ======================================================

POWER_LOST = "POWER_LOST"
POWER_RESTORED = "POWER_RESTORED"

COUNTDOWN_STARTED = "COUNTDOWN_STARTED"
COUNTDOWN_CANCELLED = "COUNTDOWN_CANCELLED"

SHUTDOWN_EXECUTED = "SHUTDOWN_EXECUTED"

ESP_ONLINE = "ESP_ONLINE"
ESP_OFFLINE = "ESP_OFFLINE"

HEARTBEAT = "HEARTBEAT"

# ======================================================
# LOGGER
# ======================================================

def log_event(
    device,
    event,
    severity,
    message
):

    timestamp = datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )

    print(
        f"[{timestamp}] [{severity}] {device} - {message}",
        flush=True
    )

    insert_event(
        timestamp,
        device,
        event,
        severity,
        message
    )

    print(f"INSERT SQLITE -> {event}")

# ======================================================
# EVENT HELPERS
# ======================================================

def event_power_lost(device):

    log_event(
        device,
        POWER_LOST,
        WARNING,
        "Power Lost"
    )

def event_power_restored(device):

    log_event(
        device,
        POWER_RESTORED,
        INFO,
        "Power Restored"
    )


def event_countdown_started(device):

    log_event(
        device,
        COUNTDOWN_STARTED,
        INFO,
        "Shutdown countdown started"
    )


def event_countdown_cancelled(device):

    log_event(
        device,
        COUNTDOWN_CANCELLED,
        INFO,
        "Shutdown countdown cancelled"
    )


def event_shutdown(device):

    log_event(
        device,
        SHUTDOWN_EXECUTED,
        CRITICAL,
        "System shutdown executed"
    )


def event_esp_online(device):

    log_event(
        device,
        ESP_ONLINE,
        INFO,
        "ESP Online"
    )


def event_esp_offline(device):

    log_event(
        device,
        ESP_OFFLINE,
        WARNING,
        "ESP Offline"
    )


def event_heartbeat(device):

    log_event(
        device,
        HEARTBEAT,
        INFO,
        "Heartbeat received"
    )