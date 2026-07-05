"""Support for Big Ass Fans SenseME light."""
import logging
from typing import Any

from aiosenseme import SensemeDevice
from homeassistant.components.light import (
    ATTR_BRIGHTNESS,
    ATTR_COLOR_TEMP_KELVIN,
    ColorMode,
    LightEntity,
)
from homeassistant.const import CONF_DEVICE

from . import SensemeEntity
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, entry, async_add_entities):
    """Set up SenseME lights."""
    device = hass.data[DOMAIN][entry.entry_id][CONF_DEVICE]
    if device.has_light:
        async_add_entities([HASensemeLight(device)])


class HASensemeLight(SensemeEntity, LightEntity):
    """Representation of a Big Ass Fans SenseME light."""

    def __init__(self, device: SensemeDevice):
        """Initialize the entity."""
        self._device = device
        if device.is_light:
            name = device.name
        else:
            name = f"{device.name} Light"
        super().__init__(device, name)
        # A standalone SenseME light supports color temperature; a fan-light is
        # brightness-only. In the modern API COLOR_TEMP implies brightness.
        if device.is_light:
            self._attr_color_mode = ColorMode.COLOR_TEMP
            self._attr_supported_color_modes = {ColorMode.COLOR_TEMP}
        else:
            self._attr_color_mode = ColorMode.BRIGHTNESS
            self._attr_supported_color_modes = {ColorMode.BRIGHTNESS}

    @property
    def unique_id(self) -> str:
        """Return a unique identifier for this light."""
        return f"{self._device.uuid}-LIGHT"

    @property
    def is_on(self) -> bool:
        """Return true if light is on."""
        return self._device.light_on

    @property
    def brightness(self) -> int:
        """Return the brightness of the light."""
        light_brightness = self._device.light_brightness * 16
        if light_brightness == 256:
            light_brightness = 255
        return int(light_brightness)

    @property
    def color_temp_kelvin(self) -> int:
        """Return the color temperature value in Kelvin."""
        if not self._device.is_light:
            return None
        return int(self._device.light_color_temp)

    @property
    def min_color_temp_kelvin(self):
        """Return the warmest color temperature this light supports, in Kelvin."""
        if not self._device.is_light:
            return None
        return int(self._device.light_color_temp_min)

    @property
    def max_color_temp_kelvin(self):
        """Return the coldest color temperature this light supports, in Kelvin."""
        if not self._device.is_light:
            return None
        return int(self._device.light_color_temp_max)

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn on the light."""
        brightness = kwargs.get(ATTR_BRIGHTNESS)
        color_temp = kwargs.get(ATTR_COLOR_TEMP_KELVIN)
        if color_temp is not None:
            self._device.light_color_temp = int(color_temp)
        if brightness is None:
            # no brightness, just turn the light on
            self._device.light_on = True
        else:
            # set the brightness, which will also turn on/off light
            if brightness == 255:
                brightness = 256  # this will end up as 16 which is max
            self._device.light_brightness = int(brightness / 16)

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn off the light."""
        self._device.light_on = False
