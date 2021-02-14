"""Config flow for SenseME."""
# import asyncio
import logging

import voluptuous as vol
from aiosenseme import async_get_device_by_ip_address, discover_all
from homeassistant import config_entries
from homeassistant.core import callback

from .const import (
    CONF_DEVICE_INPUT,
    CONF_ENABLE_DIRECTION,
    CONF_ENABLE_DIRECTION_DEFAULT,
    CONF_ENABLE_WHOOSH,
    CONF_ENABLE_WHOOSH_DEFAULT,
    CONF_INFO,
    DOMAIN,
)

_LOGGER = logging.getLogger(__name__)


class SensemeFlowHandler(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle SenseME discovery config flow."""

    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_LOCAL_PUSH

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        """Get the options flow for this handler."""
        return SensemeOptionsFlowHandler(config_entry)

    def _devices_str(self):
        """Return a human readable form of all discovered devices."""
        return ", ".join(
            [
                f"`{device.name} ({device.address})`"
                for device in self._discovered_devices
                if device.uuid not in self._async_current_ids()
            ]
        )

    def _prefill_identifier(self):
        """Return IP address of one device that has not been paired with."""
        for device in self._discovered_devices:
            if device.uuid not in self._async_current_ids():
                return str(device.address)
        return ""

    def __init__(self) -> None:
        """Initialize the SenseME config flow."""
        self.config = None
        self._title = "SenseME"
        self._discovered_devices = None

    async def async_step_user(self, user_input=None):
        """Handle a flow initialized by the user."""
        # start discovery the first time through
        if self._discovered_devices is None:
            self._discovered_devices = await discover_all(5)
        device_list = self._devices_str()
        default_suggestion = self._prefill_identifier()
        errors = {}
        if user_input is not None:
            device_name = user_input[CONF_DEVICE_INPUT]
            selected_device = None
            # see if device was already discovered
            for device in self._discovered_devices:
                if device == device_name:
                    selected_device = device
                    break
            if selected_device is None:
                # try name as IP address
                selected_device = await async_get_device_by_ip_address(device_name)
            if selected_device is None:
                errors["base"] = "no_devices_found"
            elif selected_device.uuid in self._async_current_ids():
                errors["base"] = "already_configured"
            else:
                await self.async_set_unique_id(selected_device.uuid)
                return self.async_create_entry(
                    title=selected_device.name,
                    data={CONF_INFO: selected_device.get_device_info()},
                )
        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {vol.Required(CONF_DEVICE_INPUT, default=default_suggestion): str}
            ),
            errors=errors,
            description_placeholders={"devices": device_list},
        )


class SensemeOptionsFlowHandler(config_entries.OptionsFlow):
    """Handle an option flow for SenseME."""

    def __init__(self, config_entry: config_entries.ConfigEntry):
        """Initialize options flow."""
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        """Handle options flow."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONF_ENABLE_DIRECTION,
                        default=self.config_entry.options.get(
                            CONF_ENABLE_DIRECTION, CONF_ENABLE_DIRECTION_DEFAULT
                        ),
                    ): bool,
                    vol.Required(
                        CONF_ENABLE_WHOOSH,
                        default=self.config_entry.options.get(
                            CONF_ENABLE_WHOOSH, CONF_ENABLE_WHOOSH_DEFAULT
                        ),
                    ): bool,
                }
            ),
        )
