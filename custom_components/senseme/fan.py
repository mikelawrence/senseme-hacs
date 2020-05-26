"""Support for Big Ass Fans SenseME fan."""
import logging

from homeassistant.components.fan import (
    DIRECTION_FORWARD,
    DIRECTION_REVERSE,
    SPEED_OFF,
    SUPPORT_DIRECTION,
    SUPPORT_OSCILLATE,
    SUPPORT_SET_SPEED,
    FanEntity,
)
from homeassistant.core import callback
from homeassistant.helpers.dispatcher import async_dispatcher_connect

from .const import (
    CONF_ENABLE_DIRECTION,
    CONF_ENABLE_DIRECTION_DEFAULT,
    CONF_ENABLE_WHOOSH,
    CONF_ENABLE_WHOOSH_DEFAULT,
    DOMAIN,
    EVENT_SENSEME_CONFIG_UPDATE,
    UPDATE_RATE,
)

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, entry, async_add_entities):
    """Set up SenseME fans."""
    if hass.data.get(DOMAIN) is None:
        hass.data[DOMAIN] = {}
    if hass.data[DOMAIN].get("fan_devices") is None:
        hass.data[DOMAIN]["fan_devices"] = []

    async def async_discovered_devices(devices: list):
        """Async handle (re)discovered SenseME devices."""
        new_fans = []
        for device in devices:
            if device not in hass.data[DOMAIN]["fan_devices"]:
                if device.is_fan:
                    device.refreshMinutes = UPDATE_RATE
                    hass.data[DOMAIN]["fan_devices"].append(device)
                    new_fans.append(HASensemeFan(hass, entry, device))
                    _LOGGER.debug("Added new fan: %s", device.name)
                if device.is_unknown_model:
                    _LOGGER.warning(
                        "Discovered unknown SenseME device model='%s' assuming it is a fan",
                        device.model,
                    )
        if len(new_fans) > 0:
            hass.add_job(async_add_entities, new_fans)

    hass.data[DOMAIN]["discovery"].add_callback(async_discovered_devices)


class HASensemeFan(FanEntity):
    """SenseME ceiling fan component."""

    def __init__(self, hass, entry, device) -> None:
        """Initialize the entity."""

        @callback
        def options_updated():
            """Handle signals of config entry being updated."""
            self.schedule_update_ha_state()

        self.device = device
        self._entry = entry
        self._name = device.name
        async_dispatcher_connect(hass, EVENT_SENSEME_CONFIG_UPDATE, options_updated)

    @property
    def _direction_enabled(self) -> bool:
        """Return True when Direction is enabled in the options."""
        if CONF_ENABLE_DIRECTION in self._entry.options:
            return self._entry.options.get(
                CONF_ENABLE_DIRECTION, CONF_ENABLE_DIRECTION_DEFAULT
            )
        return self._entry.data.get(
            CONF_ENABLE_DIRECTION, CONF_ENABLE_DIRECTION_DEFAULT
        )

    @property
    def _whoosh_enabled(self) -> bool:
        """Return True when Whoosh is enabled in the options."""
        if CONF_ENABLE_WHOOSH in self._entry.options:
            return self._entry.options.get(
                CONF_ENABLE_WHOOSH, CONF_ENABLE_WHOOSH_DEFAULT
            )
        return self._entry.data.get(CONF_ENABLE_WHOOSH, CONF_ENABLE_WHOOSH_DEFAULT)

    async def async_added_to_hass(self):
        """Add data updated listener after this object has been initialized."""
        self.device.add_callback(self.async_write_ha_state)

    @property
    def name(self) -> str:
        """Get fan name."""
        return self._name

    @property
    def device_info(self):
        """Get device info for Home Assistant."""
        info = {
            "connections": {("mac", self.device.id)},
            "identifiers": {("token", self.device.network_token)},
            "name": self.device.name,
            "manufacturer": "Big Ass Fans",
            "model": self.device.model,
        }
        if self.device.fw_version:
            info["sw_version"] = self.device.fw_version
        return info

    @property
    def unique_id(self):
        """Return a unique identifier for this fan."""
        uid = f"{self.device.id}-FAN"
        return uid

    @property
    def should_poll(self) -> bool:
        """Fan state is pushed."""
        return False

    @property
    def device_state_attributes(self) -> dict:
        """Get the current device state attributes."""
        attributes = {
            "autocomfort": self.device.fan_autocomfort,
            "smartmode": self.device.fan_smartmode,
        }
        if self.device.room_status:
            attributes["room"] = self.device.room_name
        return attributes

    @property
    def available(self) -> bool:
        """Return True if available/operational."""
        return self.device.connected

    @property
    def is_on(self) -> bool:
        """Return true if the fan is on."""
        return self.device.fan_on

    @property
    def speed(self) -> str:
        """Set the fan speed."""
        spd = str(self.device.fan_speed)
        if spd == "0":
            spd = SPEED_OFF
        return spd

    @property
    def speed_list(self) -> list:
        """Get the list of available speeds."""
        speeds = [SPEED_OFF]
        for i in range(self.device.fan_speed_min, self.device.fan_speed_max + 1):
            speeds.append(str(i))
        return speeds

    @property
    def current_direction(self) -> str:
        """Return the fan direction."""
        if self._direction_enabled:
            direction = self.device.fan_dir
            if direction == "FWD":
                return DIRECTION_FORWARD
            return DIRECTION_REVERSE
        return None

    @property
    def oscillating(self) -> bool:
        """Return the oscillation state."""
        if self._whoosh_enabled:
            return self.device.fan_whoosh
        return None

    @property
    def supported_features(self) -> int:
        """Flag supported features."""
        supported_features = SUPPORT_SET_SPEED
        if self._whoosh_enabled:
            supported_features |= SUPPORT_OSCILLATE
        if self._direction_enabled:
            supported_features |= SUPPORT_DIRECTION
        return supported_features

    def turn_on(self, speed: str = None, **kwargs) -> None:
        """Turn the fan on with speed control."""
        if speed is None:
            # no speed, just turn the fan on
            self.device.fan_on = True
        else:
            # set the speed, which will also turn on/off fan
            if speed == "off":
                self.device.fan_speed = 0
            else:
                self.device.fan_speed = int(speed)

    def turn_off(self, **kwargs) -> None:
        """Turn the fan off."""
        self.device.fan_on = False

    def set_speed(self, speed: str) -> None:
        """Set the speed of the fan."""
        if speed == "off":
            self.device.fan_speed = 0
        else:
            self.device.fan_speed = int(speed)

    def oscillate(self, oscillating: bool) -> None:
        """Set oscillation (Whoosh on SenseME fan)."""
        if self._whoosh_enabled:
            self.device.fan_whoosh = oscillating

    def set_direction(self, direction: str) -> None:
        """Set the direction of the fan."""
        if self._direction_enabled:
            if direction == DIRECTION_FORWARD:
                self.device.fan_dir = "FWD"
            else:
                self.device.fan_dir = "REV"
