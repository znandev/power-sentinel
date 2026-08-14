import configparser
import socket

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

NOTIFICATION_ENABLED = config.getboolean(
    "notification",
    "enabled",
    fallback=False
)

TELEGRAM_ENABLED = config.getboolean(
    "notification",
    "telegram",
    fallback=False
)

BOT_TOKEN = config.get(
    "notification",
    "bot_token",
    fallback=""
)

CHAT_ID = config.get(
    "notification",
    "chat_id",
    fallback=""
)

TELEGRAM_POLLING_INTERVAL = config.getint(
    "telegram",
    "polling_interval",
    fallback=5
)

SERVER_HOSTNAME = socket.gethostname()

def get_server_ip():

    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    try:

        s.connect(("8.8.8.8", 80))

        return s.getsockname()[0]

    except Exception:

        return "UNKNOWN"

    finally:

        s.close()

SERVER_IP = get_server_ip()