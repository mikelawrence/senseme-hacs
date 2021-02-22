"""Support for Big Ass Fans SenseME occupancy sensor."""
import logging

from homeassistant.components.binary_sensor import (
    DEVICE_CLASS_OCCUPANCY,
    BinarySensorEntity,
)
from homeassistant.const import CONF_DEVICE

from .const import CONF_BINARY_SENSOR, DOMAIN

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, entry, async_add_entities):
    """Set up SenseME occupancy sensors."""
    device = hass.data[DOMAIN][entry.unique_id][CONF_DEVICE]
    if device.has_sensor:
        binary_sensor = HASensemeOccupancySensor(device)
        hass.data[DOMAIN][entry.unique_id][CONF_BINARY_SENSOR] = binary_sensor
        hass.add_job(async_add_entities, [binary_sensor])


class HASensemeOccupancySensor(BinarySensorEntity):
    """Representation of a Big Ass Fans SenseME occupancy sensor."""

    def __init__(self, device):
        """Initialize the entity."""
        self._device = device
        self._name = device.name + " Occupancy"

    async def async_added_to_hass(self):
        """Add data updated listener after this object has been initialized."""
        self._device.add_callback(self.async_write_ha_state)

    @property
    def name(self):
        """Get sensor name."""
        return self._name

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
        """Return a unique identifier for this sensor."""
        uid = f"{self._device.uuid}-SENSOR"
        return uid

    @property
    def should_poll(self) -> bool:
        """Sensor state is pushed."""
        return False

    @property
    def device_state_attributes(self) -> dict:
        """Get the current state attributes."""
        return {
            "room_name": self._device.room_name,
            "room_type": self._device.room_type,
        }

    @property
    def available(self) -> bool:
        """Return True if available/operational."""
        return self._device.available

    @property
    def is_on(self) -> bool:
        """Return true if sensor is occupied."""
        return self._device.motion_detected

    @property
    def device_class(self) -> str:
        """Return the device class."""
        return DEVICE_CLASS_OCCUPANCY
