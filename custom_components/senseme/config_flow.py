"""Config flow for SenseME."""
import logging

import voluptuous as vol

import aiosenseme
from homeassistant import config_entries
from homeassistant.core import callback

from .const import (  # pylint: disable=unused-import
    CONF_ENABLE_DIRECTION,
    CONF_ENABLE_DIRECTION_DEFAULT,
    CONF_ENABLE_WHOOSH,
    CONF_ENABLE_WHOOSH_DEFAULT,
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

    def __init__(self) -> None:
        """Initialize the SenseME config flow."""
        self.config = None
        self._title = "SenseME"

    async def async_step_user(self, user_input=None):
        """Handle a flow initialized by the user."""
        if self._async_current_entries():
            return self.async_abort(reason="single_instance_allowed")

        return await self.async_step_confirm(user_input)

    async def async_step_confirm(self, user_input=None):
        """Confirm setup."""
        if user_input is None:
            return self.async_show_form(
                step_id="confirm",
                data_schema=vol.Schema(
                    {
                        vol.Optional(
                            CONF_ENABLE_DIRECTION, default=CONF_ENABLE_DIRECTION_DEFAULT
                        ): bool,
                        vol.Optional(
                            CONF_ENABLE_WHOOSH, default=CONF_ENABLE_WHOOSH_DEFAULT
                        ): bool,
                    }
                ),
            )

        if (  # pylint: disable=no-member # https://github.com/PyCQA/pylint/issues/3167
            self.context
            and self.context.get("source") != config_entries.SOURCE_DISCOVERY
        ):
            # Get current discovered entries.
            in_progress = self._async_in_progress()

            has_devices = in_progress
            if not has_devices:
                has_devices = await aiosenseme.discover_any(1)

            if not has_devices:
                return self.async_abort(reason="no_devices_found")

            # Cancel the discovered one.
            for flow in in_progress:
                self.hass.config_entries.flow.async_abort(flow["flow_id"])
        return self.async_create_entry(title=self._title, data=user_input)

    async def async_step_discovery(self, discovery_info):
        """Handle a flow initialized by discovery."""
        if self._async_in_progress() or self._async_current_entries():
            return self.async_abort(reason="single_instance_allowed")

        return await self.async_step_confirm()

    async_step_zeroconf = async_step_discovery
    async_step_ssdp = async_step_discovery
    async_step_homekit = async_step_discovery

    async def async_step_import(self, user_input):
        """Handle a flow initialized by import."""
        if self._async_in_progress() or self._async_current_entries():
            return self.async_abort(reason="single_instance_allowed")

        return self.async_create_entry(title=self._title, data={})


class SensemeOptionsFlowHandler(config_entries.OptionsFlow):
    """Handle an option flow for SenseME."""

    def __init__(self, config_entry: config_entries.ConfigEntry):
        """Initialize options flow."""
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        """Handle options flow."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)
        if CONF_ENABLE_DIRECTION in self.config_entry.options:
            enable_direction = self.config_entry.options.get(
                CONF_ENABLE_DIRECTION, CONF_ENABLE_DIRECTION_DEFAULT
            )
        else:
            enable_direction = self.config_entry.data.get(
                CONF_ENABLE_DIRECTION, CONF_ENABLE_DIRECTION_DEFAULT
            )
        if CONF_ENABLE_WHOOSH in self.config_entry.options:
            enable_whoosh = self.config_entry.options.get(
                CONF_ENABLE_WHOOSH, CONF_ENABLE_WHOOSH_DEFAULT
            )
        else:
            enable_whoosh = self.config_entry.data.get(
                CONF_ENABLE_WHOOSH, CONF_ENABLE_WHOOSH_DEFAULT
            )
        data_schema = vol.Schema(
            {
                vol.Optional(CONF_ENABLE_DIRECTION, default=enable_direction): bool,
                vol.Optional(CONF_ENABLE_WHOOSH, default=enable_whoosh): bool,
            }
        )
        return self.async_show_form(step_id="init", data_schema=data_schema)
