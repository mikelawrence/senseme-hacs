"""Config flow for SenseME."""
import aiosenseme

from homeassistant import config_entries
from homeassistant.helpers import config_entry_flow

from .const import DOMAIN


async def _async_has_devices(hass) -> bool:
    """Return if there are devices that can be discovered."""
    return await aiosenseme.discover_any(1)


config_entry_flow.register_discovery_flow(
    DOMAIN, "SenseME", _async_has_devices, config_entries.CONN_CLASS_LOCAL_PUSH
)
