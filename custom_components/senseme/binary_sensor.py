"""Support for Big Ass Fans SenseME occupancy sensor."""
import logging
import traceback

from homeassistant.components.binary_sensor import (
    DEVICE_CLASS_OCCUPANCY,
    BinarySensorDevice,
)

from .const import DOMAIN, UPDATE_RATE

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, entry, async_add_entities):
    """Set up SenseME sensors."""
    if hass.data.get(DOMAIN) is None:
        hass.data[DOMAIN] = {}
    if hass.data[DOMAIN].get("sensor_devices") is None:
        hass.data[DOMAIN]["sensor_devices"] = []

    async def async_discovered_fans(fans: list):
        """Async handle a (re)discovered SenseME fans."""
        new_sensors = []
        for fan in fans:
            try:
                if fan not in hass.data[DOMAIN]["sensor_devices"]:
                    if "Haiku Fan" in fan.model:
                        fan.refreshMinutes = UPDATE_RATE
                        hass.data[DOMAIN]["sensor_devices"].append(fan)
                        sensor = HASensemeOccupancySensor(fan)
                        new_sensors.append(sensor)
                        _LOGGER.debug("Added new sensor: %s" % sensor.name)
                    else:
                        # ignore a sensor by adding it to the sensor_devices
                        # list and NOT adding it with async_add_entities()
                        hass.data[DOMAIN]["sensor_devices"].append(fan)
            except Exception:
                _LOGGER.error("Discovered fan error\n%s" % traceback.format_exc())
        if len(new_sensors) > 0:
            hass.add_job(async_add_entities, new_sensors)

    hass.data[DOMAIN]["discovery"].add_callback(async_discovered_fans)


class HASensemeOccupancySensor(BinarySensorDevice):
    """Representation of a Big Ass Fans SenseME occupancy sensor."""

    def __init__(self, device):
        """Initialize the entity."""
        self.device = device
        self._name = device.name + " Occupancy"

    async def async_added_to_hass(self):
        """Add data updated listener after this object has been initialized."""
        self.device.add_callback(lambda: self.async_write_ha_state())

    @property
    def name(self):
        """Get sensor name."""
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
        """Return a unique identifier for this sensor."""
        uid = f"{self.device.id}-SENSOR"
        return uid

    @property
    def should_poll(self) -> bool:
        """This sensor's state is pushed."""
        return False

    @property
    def device_state_attributes(self) -> dict:
        """Gets the current state attributes."""
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
        """Return true if sensor is occupied."""
        return self.device.motion_sensor

    @property
    def device_class(self) -> str:
        """Return the device class."""
        return DEVICE_CLASS_OCCUPANCY
