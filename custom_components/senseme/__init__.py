"""The SenseME integration."""
import asyncio
import logging

from aiosenseme import SensemeDiscovery
from aiosenseme import __version__ as aiosenseme_version
from homeassistant.components.binary_sensor import DOMAIN as BINARYSENSOR_DOMAIN
from homeassistant.components.fan import DOMAIN as FAN_DOMAIN
from homeassistant.components.light import DOMAIN as LIGHT_DOMAIN
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.dispatcher import async_dispatcher_send

from .const import DISCOVERY_UPDATE_RATE, DOMAIN, EVENT_SENSEME_CONFIG_UPDATE
from .version import __version__

PLATFORMS = [FAN_DOMAIN, LIGHT_DOMAIN, BINARYSENSOR_DOMAIN]

_LOGGER = logging.getLogger(__name__)


async def async_setup(hass: HomeAssistant, config: dict):
    """Set up the SenseME component."""
    if config.get(DOMAIN) is not None:
        _LOGGER.error(
            "Configuration of senseme integration via yaml is depreciated,"
            " instead use Home Assistant frontend to add this integration"
        )
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Set up SenseME from a config entry."""
    _LOGGER.debug("Integration=v%s, aiosenseme==%s", __version__, aiosenseme_version)
    hass.data[DOMAIN] = {}
    # start SenseME discovery
    discovery = SensemeDiscovery(True, DISCOVERY_UPDATE_RATE)
    hass.data[DOMAIN]["discovery"] = discovery
    discovery.start()
    for component in PLATFORMS:
        hass.async_create_task(
            hass.config_entries.async_forward_entry_setup(entry, component)
        )
    await asyncio.sleep(0.1)
    entry.add_update_listener(async_config_entry_updated)
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
        hass.data[DOMAIN]["discovery"].remove_discovered_devices()
        hass.data[DOMAIN]["discovery"] = None
        hass.data[DOMAIN]["fan_devices"] = []
        hass.data[DOMAIN]["light_devices"] = []
        hass.data[DOMAIN]["sensor_devices"] = []

    return True


async def async_config_entry_updated(hass, entry) -> None:
    """Handle signals of config entry being updated."""
    async_dispatcher_send(hass, EVENT_SENSEME_CONFIG_UPDATE)
