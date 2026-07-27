import configparser

config = configparser.ConfigParser()

config.read("config.ini")

HOST = config["server"]["host"]

PORT = config.getint("server","port")

COUNTDOWN = config.getint(
    "shutdown",
    "countdown"
)

TEST_MODE = config.getboolean(
    "shutdown",
    "test_mode"
)

HEARTBEAT_TIMEOUT = config.getint(
    "heartbeat",
    "timeout"
)

TITLE = config["dashboard"]["title"]