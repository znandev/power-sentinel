import configparser

config = configparser.ConfigParser()

config.read("config.ini")

HOST = config["server"]["host"]

PORT = config.getint("server","port")

HEARTBEAT_TIMEOUT = config.getint(
    "heartbeat",
    "timeout"
)

ESP_TIMEOUT = config.getint(
    "ESP",
    "esp_timeout"
)

TITLE = config["dashboard"]["title"]

# ======================================================
# SHUTDOWN CONFIGURATION
# ======================================================

SHUTDOWN_ENABLED = config.getboolean(
    "shutdown",
    "shutdown_enabled",
    fallback=False
)

COUNTDOWN = config.getint(
    "shutdown",
    "countdown",
    fallback=60
)

STOP_SERVICES = config.getboolean(
    "shutdown",
    "stop_services",
    fallback=False
)

SERVICE_TIMEOUT = config.getint(
    "shutdown",
    "service_timeout",
    fallback=5
)

SERVICES = [

    service.strip()

    for service in config.get(
        "shutdown",
        "services",
        fallback=""
    ).split(",")

    if service.strip()

]