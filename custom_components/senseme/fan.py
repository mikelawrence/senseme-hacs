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

from . import SensemeEntity
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


class HASensemeFan(SensemeEntity, FanEntity):
    """SenseME ceiling fan component."""

    def __init__(self, entry, device) -> None:
        """Initialize the entity."""
        super().__init__(device, device.name)
        self._entry = entry

    async def async_added_to_hass(self):
        """Add data updated listener after this object has been initialized."""
        self.device.add_callback(self.async_write_ha_state)

    @property
    def unique_id(self):
        """Return a unique identifier for this fan."""
        return f"{self.device.uuid}-FAN"

    @property
    def device_state_attributes(self) -> dict:
        """Get the current device state attributes."""
        return {
            "auto_comfort": self._device.fan_autocomfort.capitalize(),
            "smartmode": self._device.fan_smartmode.capitalize(),
            "motion_control": "On" if self._device.motion_fan_auto else "Off",
            **super().device_state_attributes,
        }

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

    async def async_set_percentage(self, percentage: int) -> None:
        """Set the speed of the fan, as a percentage."""
        self._device.fan_speed = math.ceil(
            percentage_to_ranged_value(self._device.fan_speed_limits, percentage)
        )

    async def async_turn_on(
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

    async def async_turn_off(self, **kwargs) -> None:
        """Turn the fan off."""
        self._device.fan_on = False

    async def async_set_preset_mode(self, preset_mode: str) -> None:
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

    async def async_set_direction(self, direction: str) -> None:
        """Set the direction of the fan."""
        if direction == DIRECTION_FORWARD:
            self._device.fan_dir = "FWD"
        else:
            self._device.fan_dir = "REV"
