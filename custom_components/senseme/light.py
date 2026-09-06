"""Support for Big Ass Fans SenseME light."""
import logging
from typing import Any

from aiosenseme import SensemeDevice
from homeassistant.components.light import ColorMode, LightEntity
from homeassistant.const import CONF_DEVICE

from . import SensemeEntity
from .const import DOMAIN

ATTR_BRIGHTNESS = "brightness"
ATTR_COLOR_TEMP = "color_temp"

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

    @property
    def unique_id(self) -> str:
        """Return a unique identifier for this light."""
        return f"{self._device.uuid}-LIGHT"

    @property
    def is_on(self) -> bool:
        """Return true if light is on."""
        return self._device.light_on

    @property
    def color_mode(self) -> ColorMode:
        """Return the color mode of the light."""
        if self._device.is_light:
            return ColorMode.COLOR_TEMP
        return ColorMode.BRIGHTNESS

    @property
    def supported_color_modes(self) -> set[ColorMode]:
        """Flag supported color modes."""
        if self._device.is_light:
            return {ColorMode.COLOR_TEMP}
        return {ColorMode.BRIGHTNESS}

    @property
    def brightness(self) -> int:
        """Return the brightness of the light."""
        light_brightness = self._device.light_brightness * 16
        if light_brightness == 256:
            light_brightness = 255
        return int(light_brightness)

    @property
    def color_temp(self) -> int:
        """Return the color temp value in mireds."""
        if not self._device.is_light:
            return None
        color_temp = int(round(1000000.0 / float(self._device.light_color_temp)))
        return color_temp

    @property
    def min_mireds(self):
        """Return the coldest color temp that this light supports."""
        if not self._device.is_light:
            return None
        color_temp = int(round(1000000.0 / float(self._device.light_color_temp_max)))
        return color_temp

    @property
    def max_mireds(self):
        """Return the warmest color temp that this light supports."""
        if not self._device.is_light:
            return None
        color_temp = int(round(1000000.0 / float(self._device.light_color_temp_min)))
        return color_temp

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn on the light."""
        brightness = kwargs.get(ATTR_BRIGHTNESS)
        color_temp = kwargs.get(ATTR_COLOR_TEMP)
        if color_temp is not None:
            self._device.light_color_temp = int(round(1000000.0 / float(color_temp)))
        if brightness is None:
            self._device.light_on = True
        else:
            if brightness == 255:
                brightness = 256
            self._device.light_brightness = int(brightness / 16)

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn off the light."""
        self._device.light_on = False
