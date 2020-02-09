"""Support for Big Ass Fans with SenseME ceiling fan."""
import logging
import socket
from datetime import timedelta

from homeassistant.const import STATE_ON, STATE_OFF, STATE_UNKNOWN
from homeassistant.components.fan import (
    FanEntity,
    DOMAIN,
    SPEED_OFF,
    SUPPORT_SET_SPEED,
    SUPPORT_OSCILLATE,
    SUPPORT_DIRECTION,
    DIRECTION_FORWARD,
    DIRECTION_REVERSE,
)
from custom_components.senseme import DATA_HUBS

SCAN_INTERVAL = timedelta(seconds=15)

_LOGGER = logging.getLogger(__name__)

_VALID_SPEEDS = ["off", "1", "2", "3", "4", "5", "6", "7"]
_VALID_DIRECTIONS = [DIRECTION_FORWARD, DIRECTION_REVERSE]


# pylint: disable=unused-argument
def setup_platform(hass, config, add_devices_callback, discovery_info=None):
    """Set up the Haiku with SenseME ceiling fan platform."""
    fans = []
    for hub in hass.data[DATA_HUBS]:
        fans.append(HaikuSenseMeFan(hass, hub))
    add_devices_callback(fans)


class HaikuSenseMeFan(FanEntity):
    """Representation of a Haiku with SenseME ceiling fan."""

    def __init__(self, hass, hub) -> None:
        """Initialize the entity."""
        self.hass = hass
        self._hub = hub
        self._name = hub.friendly_name
        self._supported_features = (
            SUPPORT_SET_SPEED | SUPPORT_OSCILLATE | SUPPORT_DIRECTION
        )
        _LOGGER.debug("%s: Created HaikuSenseMeFan" % self.name)

    @property
    def name(self) -> str:
        """Get fan name."""
        return self._name

    @property
    def should_poll(self) -> bool:
        """Polling is needed for this fan."""
        return True

    @property
    def speed(self) -> str:
        return self._hub.fan_speed

    @property
    def speed_list(self) -> list:
        """Get the list of available speeds."""
        return _VALID_SPEEDS

    @property
    def is_on(self) -> bool:
        """Return true if the fan is on."""
        return self._hub.fan_on

    @property
    def oscillating(self):
        """Return the oscillation state."""
        return self._hub.whoosh_on

    @property
    def direction(self) -> str:
        """Return the fan direction."""
        return self._hub.fan_direction

    @property
    def supported_features(self) -> int:
        """Flag supported features."""
        return self._supported_features

    def turn_on(self, speed: str = None, **kwargs) -> None:
        """Turn on the fan."""
        retryCount = 2
        while retryCount != 0:
            try:
                if speed == None:
                    self._hub.fan_on = True
                else:
                    self._hub.fan_speed = speed
                break
            except socket.error as e:
                retryCount -= 1
                if retryCount == 0:
                    raise

    def turn_off(self, **kwargs) -> None:
        """Turn off the fan."""
        retryCount = 2
        while retryCount != 0:
            try:
                self._hub.fan_on = False
                break
            except socket.error as e:
                retryCount -= 1
                if retryCount == 0:
                    raise

    def set_speed(self, speed: str) -> None:
        """Set the speed of the fan."""
        # Validate speed
        if speed in _VALID_SPEEDS or speed == STATE_UNKNOWN:
            retryCount = 2
            while retryCount != 0:
                try:
                    self._hub.fan_speed = speed
                    break
                except socket.error as e:
                    retryCount -= 1
                    if retryCount == 0:
                        raise
        else:
            _LOGGER.error(
                "Received invalid speed: %s. " + "Expected: %s.",
                speed,
                self._speed_list,
            )
            self._speed = None

    def oscillate(self, oscillating: bool) -> None:
        """Set oscillation."""
        retryCount = 2
        while retryCount != 0:
            try:
                self._hub.whoosh_on = oscillating
                break
            except socket.error as e:
                retryCount -= 1
                if retryCount == 0:
                    raise

    def set_direction(self, direction: str) -> None:
        """Set the direction of the fan."""
        if direction in _VALID_DIRECTIONS:
            retryCount = 2
            while retryCount != 0:
                try:
                    self._hub.fan_direction = direction
                    break
                except socket.error as e:
                    retryCount -= 1
                    if retryCount == 0:
                        raise
        else:
            _LOGGER.error(
                "Received invalid direction: %s. " + "Expected: %s.",
                direction,
                ", ".join(_VALID_DIRECTIONS),
            )

    def update(self) -> None:
        """Update current fan values."""
        self._hub.update()
