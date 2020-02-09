"""Support for Big Ass Fans with SenseME platform."""
import logging
import voluptuous as vol
from datetime import timedelta

from homeassistant.const import (
    CONF_INCLUDE,
    CONF_EXCLUDE,
    CONF_NAME,
    CONF_FRIENDLY_NAME,
)
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.discovery import load_platform
from homeassistant.helpers.event import track_time_interval
from homeassistant.util import Throttle
from homeassistant.components.fan import DIRECTION_FORWARD, DIRECTION_REVERSE

DOMAIN = "senseme"

# delay between SenseMe background updates (in seconds)
SENSEME_UPDATE_DELAY = 30.0

# Fan has light default value
HAS_LIGHT_DEFAULT = True

# Component update rate
MIN_TIME_BETWEEN_UPDATES = timedelta(seconds=30)

DATA_HUBS = "fans"

CONF_MAX_NUMBER_FANS = "max_number_fans"
CONF_HAS_LIGHT = "has_light"

INCLUDE_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_NAME): cv.string,
        vol.Optional(CONF_FRIENDLY_NAME): cv.string,
        vol.Optional(CONF_HAS_LIGHT, default=HAS_LIGHT_DEFAULT): cv.boolean,
    }
)

CONFIG_SCHEMA = vol.Schema(
    {
        DOMAIN: vol.Schema(
            {
                vol.Optional(CONF_MAX_NUMBER_FANS, default=5): vol.All(
                    vol.Coerce(int), vol.Range(min=1, max=25)
                ),
                vol.Optional(CONF_INCLUDE, default=[]): vol.All(
                    cv.ensure_list, [INCLUDE_SCHEMA]
                ),
                vol.Optional(CONF_EXCLUDE, default=[]): vol.All(
                    cv.ensure_list, [cv.string]
                ),
            }
        )
    },
    extra=vol.ALLOW_EXTRA,
)

_LOGGER = logging.getLogger(__name__)


def setup(hass, config):
    """Set up the Haiku SenseME platform."""
    from senseme import discover
    from senseme import SenseMe

    # discover Haiku with SenseME fans
    devices = discover(config[DOMAIN][CONF_MAX_NUMBER_FANS], 8)
    hubs = []
    include_list = config[DOMAIN].get(CONF_INCLUDE)
    exclude_list = config[DOMAIN].get(CONF_EXCLUDE)
    if len(include_list) > 0:
        # add only included fans
        for device in devices:
            # _LOGGER.warning("Discovered fan: '%s'." % (device.name))
            for include in include_list:
                if include["name"] == device.name:
                    # _LOGGER.warning("Match include fan: '%s'.", device.name)
                    newDevice = SenseMe(
                        ip=device.ip,
                        name=device.name,
                        monitor_frequency=SENSEME_UPDATE_DELAY,
                        monitor=True,
                    )
                    hubs.append(
                        SenseMeHub(
                            newDevice,
                            include.get("friendly_name"),
                            include["has_light"],
                        )
                    )
                    friendly_name = include.get("friendly_name")
                    if not friendly_name:
                        friendly_name = device.name
                    # _LOGGER.info("Added included fan: '%s' as '%s' %s." %
                    #              (device.name, friendly_name, "with light" if
                    #              include['has_light'] else "without light"))
        # make sure all included fans were discovered
        for include in include_list:
            discovered = False
            for hub in hubs:
                if include["name"] == hub.name:
                    discovered = True
                    break
            if discovered == False:
                _LOGGER.error("Included fan not found: '%s'." % (include["name"]))
    else:
        # add only not excluded fans
        for device in devices:
            # add only if NOT excluded
            if device.name not in exclude_list:
                newDevice = SenseMe(
                    ip=device.ip,
                    name=device.name,
                    monitor_frequency=SENSEME_UPDATE_DELAY,
                    monitor=True,
                )
                hubs.append(SenseMeHub(newDevice, None, HAS_LIGHT_DEFAULT))
                # _LOGGER.debug("Added not excluded fan: '%s', %s." %
                #               (device.name, "with light" if
                #               HAS_LIGHT_DEFAULT else "without light"))
    # SenseME fan and light platforms use hub to communicate with the fan
    hass.data[DATA_HUBS] = hubs
    # Add fan and light platform
    load_platform(hass, "fan", DOMAIN, {}, config)
    load_platform(hass, "light", DOMAIN, {}, config)

    return True


def conv_bright_ha_to_lib(brightness) -> int:
    """Convert HA brightness scale 0-255 to library scale 0-16."""
    if brightness == 255:  # this will end up as 16 which is max
        brightness = 256
    return int(brightness / 16)


def conv_bright_lib_to_ha(brightness) -> int:
    """Convert library brightness scale 0-16 to HA scale 0-255."""
    brightness = int(brightness) * 16
    if brightness > 255:  # force big numbers into 8-bit int range
        brightness = 255
    return brightness


class SenseMeHub(object):
    """Data object and access to Haiku with SenseME fan."""

    def __init__(self, device, friendly_name, has_light):
        """Initialize the data object."""
        self._device = device
        self._fan_on = None
        self._fan_speed = "4"
        self._whoosh_on = None
        self._fan_direction = None
        self._light_on = None
        self._light_brightness = None
        self._friendly_name = friendly_name
        self._light_exists = has_light

    @property
    def name(self) -> str:
        """Gets name of fan."""
        return self._device.name

    @property
    def friendly_name(self) -> str:
        """Gets friendly name of fan."""
        if self._friendly_name:
            # friendly name is defined
            return self._friendly_name
        else:
            # friendly name is not defined
            return self._device.name

    @property
    def ip(self) -> str:
        """Gets IP address of fan."""
        return self._device.ip

    @property
    def light_exists(self) -> bool:
        """Gets light exists state."""
        return self._light_exists

    @property
    def fan_on(self) -> bool:
        """Gets fan on state."""
        return self._fan_on

    @fan_on.setter
    def fan_on(self, fan_on):
        """Sets fan on state."""
        if fan_on:  # fan was turned on
            self.fan_speed = "4"
        else:  # fan was turned off
            self.fan_speed = "off"

    @property
    def fan_speed(self) -> str:
        """Gets fan speed."""
        return self._fan_speed

    @fan_speed.setter
    def fan_speed(self, fan_speed):
        """Sets fan speed."""
        if fan_speed == None:  # default fan speed when not specified
            fan_speed = "4"
        self._fan_speed = fan_speed
        if fan_speed == "off":  # fan speed set to off
            self._device.speed = 0
            # turning fan off also affects whoosh state
            self._fan_on = False
            self._whoosh_on = False
        else:  # fan speed set to a number
            self._device.speed = int(fan_speed)
            self._fan_on = True

    @property
    def fan_direction(self) -> str:
        """Gets fan direction state."""
        return self._fan_direction

    @fan_direction.setter
    def fan_direction(self, fan_direction):
        """Sets fan direction state."""
        self._fan_direction = fan_direction
        direction = "FWD"
        if fan_direction != DIRECTION_FORWARD:
            direction = "REV"
        self._device._send_command(
            "<%s;FAN;DIR;SET;%s>" % (self._device.name, direction)
        )
        self._device._update_cache("FAN;DIR", direction)

    @property
    def whoosh_on(self) -> bool:
        """Gets whoosh on state."""
        return self._whoosh_on

    @whoosh_on.setter
    def whoosh_on(self, whoosh_on):
        """Sets whoosh on state."""
        self._device.whoosh = whoosh_on
        self._whoosh_on = whoosh_on

    @property
    def light_on(self) -> bool:
        """Gets current light state."""
        return self._light_on

    @light_on.setter
    def light_on(self, light_on):
        """Sets light state."""
        # changing light on state using brightness
        if light_on:  # light was turned on
            self.light_brightness = 255
        else:  # light was turned off
            self.light_brightness = 0

    @property
    def light_brightness(self) -> int:
        """Gets light brightness."""
        return self._light_brightness

    @light_brightness.setter
    def light_brightness(self, light_brightness):
        """Sets light brightness."""
        self._device.brightness = conv_bright_ha_to_lib(light_brightness)
        self._light_brightness = light_brightness
        # changing brightness also affects light on state
        if light_brightness == 0:
            self._light_on = False
        else:
            self._light_on = True

    @Throttle(MIN_TIME_BETWEEN_UPDATES)
    def update(self) -> None:
        """Get the latest status from fan."""
        self._fan_on = self._device.get_attribute("FAN;PWR") == "ON"
        self._fan_speed = self._device.get_attribute("FAN;SPD;ACTUAL")
        if self._fan_speed == "0":
            self._fan_speed = "off"
        if self._device.get_attribute("FAN;DIR") == "FWD":
            self._fan_direction = DIRECTION_FORWARD
        else:
            self._fan_direction = DIRECTION_REVERSE
        self._whoosh_on = self._device.get_attribute("FAN;WHOOSH;STATUS") == "ON"
        if self._light_exists:
            self._light_on = self._device.get_attribute("LIGHT;PWR") == "ON"
            self._light_brightness = conv_bright_lib_to_ha(
                self._device.get_attribute("LIGHT;LEVEL;ACTUAL")
            )
        # _LOGGER.debug("SenseMe: Updated fan '%s'." % self._device.name)
        return True
