"""Support for Big Ass Fans SenseME fan."""
import logging
import math
from typing import Any, List, Optional

from homeassistant.components.fan import (
    DIRECTION_FORWARD,
    DIRECTION_REVERSE,
    SPEED_OFF,
    SUPPORT_DIRECTION,
    SUPPORT_SET_SPEED,
    FanEntity,
)
from homeassistant.const import CONF_DEVICE
from homeassistant.core import callback
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.util.percentage import (
    percentage_to_ranged_value,
    ranged_value_to_percentage,
)

from .const import (
    CONF_FAN,
    DOMAIN,
    PRESET_MODE_NONE,
    PRESET_MODE_SLEEP,
    PRESET_MODE_WHOOSH,
)

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, entry, async_add_entities):
    """Set up SenseME fans."""
    device = hass.data[DOMAIN][entry.unique_id][CONF_DEVICE]
    if device.is_fan:
        fan = HASensemeFan(entry, device)
        hass.data[DOMAIN][entry.unique_id][CONF_FAN] = fan
        hass.add_job(async_add_entities, [fan])


async def async_unload_entry(hass, entry):
    """Unload a config entry."""
    bridge = hass.data[DOMAIN].pop(entry.data["host"])
    return await bridge.async_reset()


class HASensemeFan(FanEntity):
    """SenseME ceiling fan component."""

    def __init__(self, entry, device) -> None:
        """Initialize the entity."""

        async def options_updated():
            """Handle signals of config entry being updated."""
            print(f"Fan Options Updated {self._entry.options}")
            self.schedule_update_ha_state()

        self._device = device
        self._entry = entry
        self.unsub = entry.add_update_listener(options_updated)

    async def async_added_to_hass(self):
        """Add data updated listener after this object has been initialized."""
        self._device.add_callback(self.async_write_ha_state)

    @property
    def name(self) -> str:
        """Get fan name."""
        return self._device.name

    @property
    def device_info(self):
        """Get device info for Home Assistant."""
        return {
            "connections": {("mac", self._device.mac)},
            "identifiers": {("uuid", self._device.uuid)},
            "name": self._device.name,
            "manufacturer": "Big Ass Fans",
            "model": self._device.model,
            "sw_version": self._device.fw_version,
        }

    @property
    def unique_id(self):
        """Return a unique identifier for this fan."""
        uid = f"{self._device.uuid}-FAN"
        return uid

    @property
    def should_poll(self) -> bool:
        """Fan state is pushed."""
        return False

    @property
    def device_state_attributes(self) -> dict:
        """Get the current device state attributes."""
        return {
            "room_name": self._device.room_name,
            "room_type": self._device.room_type,
            "auto_comfort": self._device.fan_autocomfort.capitalize(),
            "smartmode": self._device.fan_smartmode.capitalize(),
            "motion_control": "On" if self._device.motion_fan_auto else "Off",
        }

    @property
    def available(self) -> bool:
        """Return True if available/operational."""
        return self._device.available

    @property
    def is_on(self) -> bool:
        """Return true if the fan is on."""
        return self._device.fan_on

    @property
    def current_direction(self) -> str:
        """Return the fan direction."""
        direction = self._device.fan_dir
        if direction == "FWD":
            return DIRECTION_FORWARD
        return DIRECTION_REVERSE

    @property
    def supported_features(self) -> int:
        """Flag supported features."""
        supported_features = SUPPORT_SET_SPEED | SUPPORT_DIRECTION
        return supported_features

    @property
    def percentage(self) -> str:
        """Return the current speed."""
        return ranged_value_to_percentage(
            self._device.fan_speed_limits, self._device.fan_speed
        )

    @property
    def preset_mode(self) -> Optional[str]:
        """Return the current preset mode."""
        if self._device.fan_whoosh_mode:
            return PRESET_MODE_WHOOSH
        if self._device.sleep_mode:
            return PRESET_MODE_SLEEP
        return PRESET_MODE_NONE

    @property
    def preset_modes(self) -> Optional[List[str]]:
        """Return a list of available preset modes."""
        return [PRESET_MODE_NONE, PRESET_MODE_WHOOSH, PRESET_MODE_SLEEP]

    def set_percentage(self, percentage: int) -> None:
        """Set the speed of the fan, as a percentage."""
        self._device.fan_speed = math.ceil(
            percentage_to_ranged_value(self._device.fan_speed_limits, percentage)
        )

    def turn_on(
        self,
        speed: Optional[str] = None,
        percentage: Optional[int] = None,
        preset_mode: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        """Turn the fan on with speed control."""
        if preset_mode is not None:
            self.set_preset_mode(preset_mode)
            if preset_mode == PRESET_MODE_WHOOSH:
                self._device.sleep_mode = True
                return
        if percentage is None:
            percentage = 25

        self.set_percentage(percentage)

    def turn_off(self, **kwargs) -> None:
        """Turn the fan off."""
        self._device.fan_on = False

    def set_preset_mode(self, preset_mode: str) -> None:
        """Set the preset mode of the fan."""
        if preset_mode == PRESET_MODE_NONE:
            self._device.sleep_mode = False
            self._device.fan_whoosh_mode = False
            return
        if preset_mode == PRESET_MODE_WHOOSH:
            self._device.fan_whoosh_mode = True
            return
        if preset_mode == PRESET_MODE_SLEEP:
            self._device.sleep_mode = True
            return
        raise ValueError(f"Invalid preset mode: {preset_mode}")

    def set_direction(self, direction: str) -> None:
        """Set the direction of the fan."""
        if direction == DIRECTION_FORWARD:
            self._device.fan_dir = "FWD"
        else:
            self._device.fan_dir = "REV"
