"""Config flow for SenseME."""
from aiosenseme import Discover_Any

from homeassistant import config_entries
from homeassistant.helpers import config_entry_flow

from .const import DOMAIN


async def _async_has_devices(hass) -> bool:
    """Return if there are devices that can be discovered."""
    return await Discover_Any(1)


config_entry_flow.register_discovery_flow(
    DOMAIN, "SenseME", _async_has_devices, config_entries.CONN_CLASS_LOCAL_PUSH
)
