"""The SenseME integration."""
import asyncio
import logging

from aiosenseme import SensemeDevice
from aiosenseme import __version__ as aiosenseme_version
from aiosenseme import async_get_device_by_device_info
from homeassistant.components.binary_sensor import DOMAIN as BINARYSENSOR_DOMAIN
from homeassistant.components.fan import DOMAIN as FAN_DOMAIN
from homeassistant.components.light import DOMAIN as LIGHT_DOMAIN
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_DEVICE
from homeassistant.core import HomeAssistant
from homeassistant.helpers.dispatcher import async_dispatcher_send

from .const import (
    CONF_INFO,
    DOMAIN,
    UPDATE_RATE,
)

PLATFORMS = [FAN_DOMAIN, LIGHT_DOMAIN, BINARYSENSOR_DOMAIN]

_LOGGER = logging.getLogger(__name__)


async def async_setup(hass: HomeAssistant, config: dict):
    """Set up the SenseME component."""
    hass.data[DOMAIN] = {}
    if config.get(DOMAIN) is not None:
        _LOGGER.error(
            "Configuration of senseme integration via yaml is deprecated, "
            "instead use Home Assistant frontend to add this integration"
        )
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Set up SenseME from a config entry."""

    async def _setup_platforms():
        """Set up platforms and initiate connection."""
        await asyncio.gather(
            *[
                hass.config_entries.async_forward_entry_setup(entry, component)
                for component in PLATFORMS
            ]
        )

    hass.data[DOMAIN][entry.unique_id] = {}
    status, device = await async_get_device_by_device_info(
        info=entry.data[CONF_INFO], start_first=True, refresh_minutes=UPDATE_RATE
    )
    if not status:
        _LOGGER.warning(
            "%s: Connect to address %s failed",
            device.name,
            device.address,
        )
    await device.async_update(not status)
    hass.data[DOMAIN][entry.unique_id][CONF_DEVICE] = device
    hass.async_create_task(_setup_platforms())
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Unload a config entry."""
    unload_ok = all(
        await asyncio.gather(
            *[
                hass.config_entries.async_forward_entry_unload(entry, component)
                for component in PLATFORMS
            ]
        )
    )
    if unload_ok:
        hass.data[DOMAIN][entry.unique_id][CONF_DEVICE].stop()
        hass.data[DOMAIN][entry.unique_id] = None
    return True

async def async_config_entry_updated(hass, entry) -> None:
    """Handle signals of config entry being updated."""
    async_dispatcher_send(hass, EVENT_SENSEME_CONFIG_UPDATE)


class SensemeEntity:
    """Base class for senseme entities."""

    def __init__(self, device, name):
        """Initialize the entity."""
        self.device = device
        self._name = name

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
    def device_state_attributes(self) -> dict:
        """Get the current device state attributes."""
        return {
            "room_name": self._device.room_name,
            "room_type": self._device.room_type,
        }

    @property
    def available(self) -> bool:
        """Return True if available/operational."""
        return self.device.connected

    @property
    def should_poll(self) -> bool:
        """State is pushed."""
        return False

    @property
    def name(self):
        """Get name."""
        return self._name
