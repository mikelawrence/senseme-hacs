"""Support for Big Ass Fans SenseME light."""
import logging

from homeassistant.components.light import (
    ATTR_BRIGHTNESS,
    ATTR_COLOR_TEMP,
    SUPPORT_BRIGHTNESS,
    SUPPORT_COLOR_TEMP,
    LightEntity,
)

from .const import DOMAIN, UPDATE_RATE

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, entry, async_add_entities):
    """Set up SenseME lights."""
    if not hass.data.get(DOMAIN):
        hass.data[DOMAIN] = {}
    if not hass.data[DOMAIN].get("light_devices"):
        hass.data[DOMAIN]["light_devices"] = []

    async def async_discovered_devices(devices: list):
        """Async handle a (re)discovered SenseME devices."""
        new_lights = []
        for device in devices:
            if device not in hass.data[DOMAIN]["light_devices"]:
                if device.has_light:
                    device.refreshMinutes = UPDATE_RATE
                    hass.data[DOMAIN]["light_devices"].append(device)
                    light = HASensemeLight(device)
                    new_lights.append(light)
                    _LOGGER.debug("Added new light: %s", light.name)
        if len(new_lights) > 0:
            hass.add_job(async_add_entities, new_lights)

    hass.data[DOMAIN]["discovery"].add_callback(async_discovered_devices)


class HASensemeLight(LightEntity):
    """Representation of a Big Ass Fans SenseME light."""

    def __init__(self, device):
        """Initialize the entity."""
        self.device = device
        if device.is_light:
            self._name = device.name
        else:
            self._name = device.name + " Light"
        self._supported_features = SUPPORT_BRIGHTNESS
        if device.is_light:
            self._supported_features |= SUPPORT_COLOR_TEMP

    async def async_added_to_hass(self):
        """Add data updated listener after this object has been initialized."""
        self.device.add_callback(self.async_write_ha_state)

    @property
    def name(self):
        """Get light name."""
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
        """Return a unique identifier for this light."""
        uid = f"{self.device.id}-LIGHT"
        return uid

    @property
    def should_poll(self) -> bool:
        """Light state is pushed."""
        return False

    @property
    def device_state_attributes(self) -> dict:
        """Get the current device state attributes."""
        attributes = {}
        if self.device.room_status:
            attributes["room"] = self.device.room_name
        return attributes

    @property
    def available(self) -> bool:
        """Return True if available/operational."""
        return self.device.connected

    @property
    def is_on(self) -> bool:
        """Return true if light is on."""
        return self.device.light_on

    @property
    def brightness(self) -> int:
        """Return the brightness of the light."""
        light_brightness = self.device.light_brightness * 16
        if light_brightness == 256:
            light_brightness = 255
        return int(light_brightness)

    @property
    def color_temp(self):
        """Return the color temp value in mireds."""
        if not self.device.is_light:
            return None
        color_temp = int(round(1000000.0 / float(self.device.light_color_temp)))
        return color_temp

    @property
    def min_mireds(self):
        """Return the coldest color temp that this light supports."""
        if not self.device.is_light:
            return None
        color_temp = int(round(1000000.0 / float(self.device.light_color_temp_max)))
        return color_temp

    @property
    def max_mireds(self):
        """Return the warmest color temp that this light supports."""
        if not self.device.is_light:
            return None
        color_temp = int(round(1000000.0 / float(self.device.light_color_temp_min)))
        return color_temp

    @property
    def supported_features(self) -> int:
        """Flag supported features."""
        return self._supported_features

    def turn_on(self, **kwargs) -> None:
        """Turn on the light."""
        brightness = kwargs.get(ATTR_BRIGHTNESS)
        color_temp = kwargs.get(ATTR_COLOR_TEMP)
        if color_temp is not None:
            self.device.light_color_temp = int(round(1000000.0 / float(color_temp)))
        if brightness is None:
            # no brightness, just turn the light on
            self.device.light_on = True
        else:
            # set the brightness, which will also turn on/off light
            if brightness == 255:
                brightness = 256  # this will end up as 16 which is max
            self.device.light_brightness = int(brightness / 16)

    def turn_off(self, **kwargs) -> None:
        """Turn off the light."""
        self.device.light_on = False
