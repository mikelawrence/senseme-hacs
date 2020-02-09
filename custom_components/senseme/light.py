"""Support for Big Ass Fans with SenseME light."""
import logging
import socket
from datetime import timedelta

from homeassistant.components.light import Light, ATTR_BRIGHTNESS, SUPPORT_BRIGHTNESS
from custom_components.senseme import DATA_HUBS

SCAN_INTERVAL = timedelta(seconds=15)

_LOGGER = logging.getLogger(__name__)


def setup_platform(hass, config, add_devices_callback, discovery_info=None):
    """Set up the Haiku with SenseME ceiling fan light platform."""
    lights = []
    for hub in hass.data[DATA_HUBS]:
        # add the light only if one is installed in the fan
        if hub.light_exists:
            lights.append(HaikuSenseMeLight(hass, hub))
    add_devices_callback(lights)


class HaikuSenseMeLight(Light):
    """Representation of a Haiku with SenseME ceiling fan light."""

    def __init__(self, hass, hub):
        """Initialize the entity."""
        self.hass = hass
        self._hub = hub
        self._name = hub.friendly_name + " Light"
        self._supported_features = SUPPORT_BRIGHTNESS
        _LOGGER.debug("%s: Created HaikuSenseMeLight" % self.name)

    @property
    def name(self):
        """Get light name."""
        return self._name

    @property
    def should_poll(self) -> bool:
        """Polling needed for this light."""
        return True

    @property
    def brightness(self) -> int:
        """Return the brightness of the light."""
        return self._hub.light_brightness

    @property
    def is_on(self) -> bool:
        """Return true if light is on."""
        return self._hub.light_on

    @property
    def supported_features(self) -> int:
        """Flag supported features."""
        return self._supported_features

    def turn_on(self, **kwargs) -> None:
        """Turn on the light."""
        brightness = kwargs.get(ATTR_BRIGHTNESS)
        if brightness == None:  # use default of 255 when unspecified
            brightness = 255
        retryCount = 2
        while retryCount != 0:
            try:
                self._hub.light_brightness = brightness
                break
            except socket.error as e:
                retryCount -= 1
                if retryCount == 0:
                    raise
        _LOGGER.debug("%s: Turn light on. Brightness: %d" % (self._name, brightness))

    def turn_off(self, **kwargs) -> None:
        """Turn off the light."""
        retryCount = 2
        while retryCount != 0:
            try:
                self._hub.light_on = False
                break
            except socket.error as e:
                retryCount -= 1
                if retryCount == 0:
                    raise
        _LOGGER.debug("%s: Turn light off." % self._name)

    def update(self) -> None:
        """Update current light values."""
        self._hub.update()
