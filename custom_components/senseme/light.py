"""Support for Big Ass Fans SenseME light."""
import logging
import traceback

from homeassistant.components.light import (
    ATTR_BRIGHTNESS,
    SUPPORT_BRIGHTNESS,
    Light,
)

from .const import DOMAIN, UPDATE_RATE

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, entry, async_add_entities):
    """Set up SenseME lights."""
    if not hass.data.get(DOMAIN):
        hass.data[DOMAIN] = {}
    if not hass.data[DOMAIN].get("light_devices"):
        hass.data[DOMAIN]["light_devices"] = []

    async def async_discovered_fans(fans: list):
        """Async handle a (re)discovered SenseME fans."""
        new_lights = []
        for fan in fans:
            try:
                if fan not in hass.data[DOMAIN]["light_devices"]:
                    if fan.has_light:
                        fan.refreshMinutes = UPDATE_RATE
                        hass.data[DOMAIN]["light_devices"].append(fan)
                        light = HASensemeLight(fan)
                        new_lights.append(light)
                        _LOGGER.debug("Added new light: %s" % light.name)
            except Exception:
                _LOGGER.error("Discovered fan error\n%s" % traceback.format_exc())
        if len(new_lights) > 0:
            hass.add_job(async_add_entities, new_lights)

    hass.data[DOMAIN]["discovery"].add_callback(async_discovered_fans)


class HASensemeLight(Light):
    """Representation of a Big Ass Fans SenseME light."""

    def __init__(self, device):
        """Initialize the entity."""
        self.device = device
        self._name = device.name + " Light"
        self._supported_features = SUPPORT_BRIGHTNESS

    async def async_added_to_hass(self):
        """Add data updated listener after this object has been initialized."""
        self.device.add_callback(lambda: self.async_write_ha_state())

    @property
    def name(self):
        """Get light name."""
        return self._name

    @property
    def device_info(self):
        """Get device info for Home Assistant."""
        info = {
            "connections": {("mac", self.device.id)},
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
        """This lights's state is pushed."""
        return False

    @property
    def device_state_attributes(self) -> dict:
        """Gets the current device state attributes."""
        attributes = {}
        if self.device.group_status:
            attributes["group"] = self.device.group_name
        return attributes

    @property
    def available(self) -> bool:
        """Return True if available (operational)."""
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
            light_brightness == 255
        return int(light_brightness)

    @property
    def supported_features(self) -> int:
        """Flag supported features."""
        return self._supported_features

    def turn_on(self, **kwargs) -> None:
        """Turn on the light."""
        brightness = kwargs.get(ATTR_BRIGHTNESS)
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
