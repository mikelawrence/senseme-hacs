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

from .const import DOMAIN, UPDATE_RATE


_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, entry, async_add_entities):
    """Set up SenseME fans."""
    if hass.data.get(DOMAIN) is None:
        hass.data[DOMAIN] = {}
    if hass.data[DOMAIN].get("fan_devices") is None:
        hass.data[DOMAIN]["fan_devices"] = []

    async def async_discovered_fans(fans: list):
        """Async handle (re)discovered SenseME fans."""
        new_fans = []
        for fan in fans:
            if fan not in hass.data[DOMAIN]["fan_devices"]:
                fan.refreshMinutes = UPDATE_RATE
                hass.data[DOMAIN]["fan_devices"].append(fan)
                new_fans.append(HASensemeFan(fan))
                _LOGGER.debug("Added new fan: %s", fan.name)
                if "Haiku" not in fan.model and "Fan" not in fan.model:
                    _LOGGER.warning(
                        "Discovered unknown SenseME device model='%s'", fan.model
                    )
        if len(new_fans) > 0:
            hass.add_job(async_add_entities, new_fans)

    hass.data[DOMAIN]["discovery"].add_callback(async_discovered_fans)


class HASensemeFan(FanEntity):
    """SenseME ceiling fan component."""

    def __init__(self, device) -> None:
        """Initialize the entity."""
        self.device = device
        self._name = device.name
        self._supported_features = (
            SUPPORT_SET_SPEED | SUPPORT_OSCILLATE | SUPPORT_DIRECTION
        )

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
        direction = self.device.fan_dir
        if direction == "FWD":
            return DIRECTION_FORWARD
        return DIRECTION_REVERSE

    @property
    def oscillating(self) -> bool:
        """Return the oscillation state."""
        return self.device.fan_whoosh

    @property
    def supported_features(self) -> int:
        """Flag supported features."""
        return self._supported_features

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
        self.device.fan_whoosh = oscillating

    def set_direction(self, direction: str) -> None:
        """Set the direction of the fan."""
        if direction == DIRECTION_FORWARD:
            self.device.fan_dir = "FWD"
        else:
            self.device.fan_dir = "REV"
