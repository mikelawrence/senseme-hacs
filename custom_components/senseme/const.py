"""Constants for the SenseME integration."""
DOMAIN = "senseme"

# Periodic discovery update rate in minutes
DISCOVERY_UPDATE_RATE = 5

# Periodic fan update rate in minutes
UPDATE_RATE = 1

# Custom config changes event
EVENT_SENSEME_CONFIG_UPDATE = "senseme_config_updated"

# Options
CONF_ENABLE_WHOOSH = "enable_whoosh"
CONF_ENABLE_WHOOSH_DEFAULT = True
CONF_ENABLE_DIRECTION = "enable_direction"
CONF_ENABLE_DIRECTION_DEFAULT = True

# flow
CONF_DEVICE_INPUT = "device_input"

# data storage
CONF_INFO = "info"
CONF_FAN = "fan"
CONF_LIGHT = "light"
CONF_BINARY_SENSOR = "binary_sensor"

# Fan Preset Modes
PRESET_MODE_WHOOSH = "Whoosh"
PRESET_MODE_SLEEP = "Sleep"
PRESET_MODE_NORMAL = "Normal"
