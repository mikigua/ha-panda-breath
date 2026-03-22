"""Constants for Panda Breath integration."""

DOMAIN = "panda_breath"

# Default connection settings
DEFAULT_HOST = "pandabreath.local"
DEFAULT_PORT = 80
DEFAULT_SCAN_INTERVAL = 60  # seconds

# WebSocket
WS_PATH = "/ws"
WS_TIMEOUT = 10
WS_RECONNECT_INTERVAL = 30

# mDNS hostname candidates to try during discovery
MDNS_HOSTNAMES = [
    "pandabreath.local",
    "PandaBreath.local",
    "panda-breath.local",
]

# Work modes
WORK_MODE_AUTO = 1
WORK_MODE_ON = 2
WORK_MODE_DRYING = 3

WORK_MODE_MAP = {
    WORK_MODE_AUTO: "Auto",
    WORK_MODE_ON: "Power On",
    WORK_MODE_DRYING: "Filament Drying",
}

WORK_MODE_REVERSE_MAP = {v: k for k, v in WORK_MODE_MAP.items()}

# Entity keys
KEY_WORK_ON = "work_on"
KEY_WORK_MODE = "work_mode"
KEY_SET_TEMP = "set_temp"
KEY_FILTER_TEMP = "filtertemp"
KEY_HOTBED_TEMP = "hotbedtemp"
KEY_WAREHOUSE_TEMPER = "warehouse_temper"
KEY_FW_VERSION = "fw_version"

# Coordinator update interval
UPDATE_INTERVAL = DEFAULT_SCAN_INTERVAL
