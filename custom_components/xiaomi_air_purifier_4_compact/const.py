"""Constants for the Xiaomi Smart Air Purifier 4 Compact integration."""

DOMAIN = "xiaomi_air_purifier_4_compact"
DEFAULT_NAME = "Xiaomi Smart Air Purifier 4 Compact"
DEFAULT_SCAN_INTERVAL = 30  # seconds

CONF_IP = "host"
CONF_TOKEN = "token"
CONF_NAME = "name"
CONF_MAC = "mac"
CONF_MODEL = "model"
DEFAULT_MODEL = "xiaomi.airp.cpa4"
SUPPORTED_MODELS = ("xiaomi.airp.cpa4",)

# miIO transport: one request waits DEVICE_TIMEOUT seconds and is retried
# DEVICE_RETRIES times; the device accepts a limited number of properties
# per get_properties request.
DEVICE_TIMEOUT = 3
DEVICE_RETRIES = 1
PROPERTIES_PER_REQUEST = 10


# MIoT spec: urn:miot-spec-v2:device:air-purifier:0000A007:xiaomi-cpa4:2
class PurifierSIID:
    DEVICE_INFO = 1
    AIR_PURIFIER = 2
    ENVIRONMENT = 3
    FILTER = 4
    ALARM = 6
    PHYSICAL_CONTROLS = 8
    CUSTOM = 9
    AQI = 11
    SCREEN = 13


class PurifierPIID:
    # Air Purifier (SIID 2)
    ON = 1                      # bool
    FAULT = 2                   # 0=No Faults, 2=Motor Stuck, 3=Sensor Lost
    MODE = 4                    # 0=Auto, 1=Sleep, 2=Favorite

    # Environment (SIID 3)
    PM25_DENSITY = 4            # µg/m³, 0-600

    # Filter (SIID 4)
    FILTER_LIFE_LEVEL = 1       # %
    FILTER_USED_TIME = 3        # hours
    FILTER_LEFT_TIME = 4        # days

    # Alarm (SIID 6)
    ALARM = 1                   # bool, button beeps

    # Physical Control Locked (SIID 8)
    PHYSICAL_LOCK = 1           # bool

    # Custom Service (SIID 9)
    MOTOR_SPEED = 1             # rpm, 0-2500
    COUNTRY_CODE = 10           # writable region code, never written
    FAVORITE_LEVEL = 11         # 0-14, fan level used in Favorite mode

    # Screen (SIID 13)
    BRIGHTNESS = 2              # 0=Close, 1=Bright, 2=Brightness


class PurifierAIID:
    # Filter (SIID 4)
    RESET_FILTER_LIFE = 1       # In: []


class Prop:
    """Keys of the polled properties in the coordinator data."""

    ON = "on"
    FAULT = "fault"
    MODE = "mode"
    PM25 = "pm25"
    FILTER_LIFE = "filter_life"
    FILTER_USED_TIME = "filter_used_time"
    FILTER_LEFT_TIME = "filter_left_time"
    ALARM = "alarm"
    CHILD_LOCK = "child_lock"
    MOTOR_SPEED = "motor_speed"
    FAVORITE_LEVEL = "favorite_level"
    BRIGHTNESS = "brightness"


# key -> (siid, piid). Left out on purpose: device information (the firmware
# answers "hello" for every siid 1 property), 9.10 country-code (changing the
# region can lock the device to another cloud), 9.12 filter-used-time-dbg
# (debug, write only) and 11.4 aqi-updata-heartbeat.
POLLED_PROPERTIES: dict[str, tuple[int, int]] = {
    Prop.ON: (PurifierSIID.AIR_PURIFIER, PurifierPIID.ON),
    Prop.FAULT: (PurifierSIID.AIR_PURIFIER, PurifierPIID.FAULT),
    Prop.MODE: (PurifierSIID.AIR_PURIFIER, PurifierPIID.MODE),
    Prop.PM25: (PurifierSIID.ENVIRONMENT, PurifierPIID.PM25_DENSITY),
    Prop.FILTER_LIFE: (PurifierSIID.FILTER, PurifierPIID.FILTER_LIFE_LEVEL),
    Prop.FILTER_USED_TIME: (PurifierSIID.FILTER, PurifierPIID.FILTER_USED_TIME),
    Prop.FILTER_LEFT_TIME: (PurifierSIID.FILTER, PurifierPIID.FILTER_LEFT_TIME),
    Prop.ALARM: (PurifierSIID.ALARM, PurifierPIID.ALARM),
    Prop.CHILD_LOCK: (PurifierSIID.PHYSICAL_CONTROLS, PurifierPIID.PHYSICAL_LOCK),
    Prop.MOTOR_SPEED: (PurifierSIID.CUSTOM, PurifierPIID.MOTOR_SPEED),
    Prop.FAVORITE_LEVEL: (PurifierSIID.CUSTOM, PurifierPIID.FAVORITE_LEVEL),
    Prop.BRIGHTNESS: (PurifierSIID.SCREEN, PurifierPIID.BRIGHTNESS),
}

# 2.4 mode
MODE_AUTO = "auto"
MODE_SLEEP = "sleep"
MODE_FAVORITE = "favorite"
MODE_TO_INT = {MODE_AUTO: 0, MODE_SLEEP: 1, MODE_FAVORITE: 2}
INT_TO_MODE = {v: k for k, v in MODE_TO_INT.items()}

# 9.11 favorite level
FAVORITE_LEVEL_MIN = 0
FAVORITE_LEVEL_MAX = 14

# 2.2 fault
FAULT_TO_STATE = {0: "no_fault", 2: "motor_stuck", 3: "sensor_lost"}

# 13.2 screen brightness
BRIGHTNESS_TO_INT = {"off": 0, "dim": 1, "bright": 2}
INT_TO_BRIGHTNESS = {v: k for k, v in BRIGHTNESS_TO_INT.items()}
