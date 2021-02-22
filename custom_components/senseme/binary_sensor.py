"""Support for Big Ass Fans SenseME occupancy sensor."""
import logging

from homeassistant.components.binary_sensor import (
    DEVICE_CLASS_OCCUPANCY,
    BinarySensorEntity,
)

from . import SensemeEntity
from .const import DOMAIN, UPDATE_RATE

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, entry, async_add_entities):
    """Set up SenseME occupancy sensors."""
    if hass.data[DOMAIN].get("sensor_devices") is None:
        hass.data[DOMAIN]["sensor_devices"] = []

    async def async_discovered_devices(devices: list):
        """Async handle a (re)discovered SenseME devices."""
        new_sensors = []
        for device in devices:
            if device not in hass.data[DOMAIN]["sensor_devices"]:
                if device.has_sensor:
                    device.refreshMinutes = UPDATE_RATE
                    hass.data[DOMAIN]["sensor_devices"].append(device)
                    sensor = HASensemeOccupancySensor(device)
                    new_sensors.append(sensor)
                    _LOGGER.debug("Added new sensor: %s", sensor.name)
        if len(new_sensors) > 0:
            hass.add_job(async_add_entities, new_sensors)

    hass.data[DOMAIN]["discovery"].add_callback(async_discovered_devices)


class HASensemeOccupancySensor(SensemeEntity, BinarySensorEntity):
    """Representation of a Big Ass Fans SenseME occupancy sensor."""

    def __init__(self, device):
        """Initialize the entity."""
        super().__init__(device, f"{device.name} Occupancy")

    async def async_added_to_hass(self):
        """Add data updated listener after this object has been initialized."""
        self.device.add_callback(self.async_write_ha_state)

    @property
    def unique_id(self):
        """Return a unique identifier for this sensor."""
        return f"{self.device.id}-SENSOR"

    @property
    def is_on(self) -> bool:
        """Return true if sensor is occupied."""
        return self.device.motion_sensor

    @property
    def device_class(self) -> str:
        """Return the device class."""
        return DEVICE_CLASS_OCCUPANCY
