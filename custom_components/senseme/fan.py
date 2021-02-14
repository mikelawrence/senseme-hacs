"""Support for Big Ass Fans SenseME fan."""
import logging
from typing import Any, List, Optional

from homeassistant.components.fan import (
    DIRECTION_FORWARD,
    DIRECTION_REVERSE,
    SPEED_OFF,
    SUPPORT_DIRECTION,
    SUPPORT_PRESET_MODE,
    SUPPORT_SET_SPEED,
    FanEntity,
)
from homeassistant.const import CONF_DEVICE
from homeassistant.core import callback
from homeassistant.helpers.dispatcher import async_dispatcher_connect

from .const import (
    CONF_FAN,
    DOMAIN,
    EVENT_SENSEME_CONFIG_UPDATE,
    PRESET_MODE_NORMAL,
    PRESET_MODE_SLEEP,
    PRESET_MODE_WHOOSH,
    UPDATE_RATE,
)

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, entry, async_add_entities):
    """Set up SenseME fans."""
    device = hass.data[DOMAIN][entry.unique_id][CONF_DEVICE]
    if device.is_fan:
        fan = HASensemeFan(entry, device)
        hass.data[DOMAIN][entry.unique_id][CONF_FAN] = fan
        hass.add_job(async_add_entities, [fan])


async def async_unload_entry(hass, entry):
    """Unload a config entry."""
    bridge = hass.data[DOMAIN].pop(entry.data["host"])
    return await bridge.async_reset()


class HASensemeFan(FanEntity):
    """SenseME ceiling fan component."""

    def __init__(self, entry, device) -> None:
        """Initialize the entity."""

        async def options_updated():
            """Handle signals of config entry being updated."""
            print(f"Fan Options Updated {self._entry.options}")
            self.schedule_update_ha_state()

        print(f"Fan Current Options = {entry.options}")
        self._device = device
        self._entry = entry
        self.unsub = entry.add_update_listener(options_updated)

    # @property
    # def _direction_enabled(self) -> bool:
    #     """Return True when Direction is enabled in the options."""
    #     return self._entry.options.get(
    #         CONF_ENABLE_DIRECTION, CONF_ENABLE_DIRECTION_DEFAULT
    #     )

    # @property
    # def _whoosh_enabled(self) -> bool:
    #     """Return True when Whoosh is enabled in the options."""
    #     return self._entry.options.get(CONF_ENABLE_WHOOSH, CONF_ENABLE_WHOOSH_DEFAULT)

    async def async_added_to_hass(self):
        """Add data updated listener after this object has been initialized."""
        self._device.add_callback(self.async_write_ha_state)

    @property
    def name(self) -> str:
        """Get fan name."""
        return self._device.name

    # @property
    # def device_info(self):
    #     """Get device info for Home Assistant."""
    #     info = {
    #         "connections": {("mac", self._device.mac)},
    #         "identifiers": {("uuid", self._device.uuid)},
    #         "name": self._device.name,
    #         "manufacturer": "Big Ass Fans",
    #         "model": self._device.model,
    #     }
    #     if self._device.fw_version:
    #         info["sw_version"] = self._device.fw_version
    #     return info

    @property
    def unique_id(self):
        """Return a unique identifier for this fan."""
        uid = f"{self._device.uuid}-FAN"
        return uid

    @property
    def should_poll(self) -> bool:
        """Fan state is pushed."""
        return False

    @property
    def device_state_attributes(self) -> dict:
        """Get the current device state attributes."""
        attributes = {
            "autocomfort": self._device.fan_autocomfort,
            "smartmode": self._device.fan_smartmode,
        }
        if self._device.room_status:
            attributes["room"] = self._device.room_name
        return attributes

    @property
    def available(self) -> bool:
        """Return True if available/operational."""
        return self._device.connected

    @property
    def is_on(self) -> bool:
        """Return true if the fan is on."""
        return self._device.fan_on

    @property
    def current_direction(self) -> str:
        """Return the fan direction."""
        direction = self._device.fan_dir
        if direction == "FWD":
            return DIRECTION_FORWARD
        return DIRECTION_REVERSE

    @property
    def supported_features(self) -> int:
        """Flag supported features."""
        # supported_features = SUPPORT_PRESET_MODE | SUPPORT_DIRECTION | SUPPORT_SET_SPEED
        supported_features = SUPPORT_SET_SPEED | SUPPORT_DIRECTION
        return supported_features

    @property
    def percentage(self) -> str:
        """Return the current speed."""
        return 50

    @property
    def preset_mode(self) -> Optional[str]:
        """Return the current preset mode."""
        if self._device.fan_whoosh:
            return PRESET_MODE_WHOOSH
        if self._device.fan_sleep_mode:
            return PRESET_MODE_SLEEP
        return PRESET_MODE_NORMAL

    @property
    def preset_modes(self) -> Optional[List[str]]:
        """Return a list of available preset modes."""
        # speeds = [SPEED_OFF]
        # for i in range(self.device.fan_speed_min, self.device.fan_speed_max + 1):
        #     speeds.append(str(i))
        return [PRESET_MODE_NORMAL, PRESET_MODE_WHOOSH, PRESET_MODE_SLEEP]

    # def set_percentage(self, percentage: int) -> None:
    #     """Set the speed of the fan, as a percentage."""
    #     return

    def turn_on(
        self,
        speed: Optional[str] = None,
        percentage: Optional[int] = None,
        preset_mode: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        """Turn the fan on with speed control."""

        if speed is None:
            # no speed, just turn the fan on
            self._device.fan_on = True
        else:
            # set the speed, which will also turn on/off fan
            if speed == "off":
                self._device.fan_speed = 0
            else:
                self._device.fan_speed = int(speed)

    def turn_off(self, **kwargs) -> None:
        """Turn the fan off."""
        self._device.fan_on = False

    # def oscillate(self, oscillating: bool) -> None:
    #     """Set oscillation (Whoosh on SenseME fan)."""
    #     if self._whoosh_enabled:
    #         self._device.fan_whoosh = oscillating

    def set_preset_mode(self, preset_mode: str) -> None:
        """Set the preset mode of the fan."""
        return

    def set_direction(self, direction: str) -> None:
        """Set the direction of the fan."""
        if direction == DIRECTION_FORWARD:
            self._device.fan_dir = "FWD"
        else:
            self._device.fan_dir = "REV"


class BaseDemoFan(FanEntity):
    """A demonstration fan component that uses legacy fan speeds."""

    def __init__(
        self,
        hass,
        unique_id: str,
        name: str,
        supported_features: int,
        preset_modes: Optional[List[str]],
        speed_list: Optional[List[str]],
    ) -> None:
        """Initialize the entity."""
        self.hass = hass
        self._unique_id = unique_id
        self._supported_features = supported_features
        self._speed = SPEED_OFF
        self._percentage = None
        self._speed_list = speed_list
        self._preset_modes = preset_modes
        self._preset_mode = None
        self._oscillating = None
        self._direction = None
        self._name = name
        if supported_features & SUPPORT_OSCILLATE:
            self._oscillating = False
        if supported_features & SUPPORT_DIRECTION:
            self._direction = "forward"

    @property
    def unique_id(self):
        """Return the unique id."""
        return self._unique_id

    @property
    def name(self) -> str:
        """Get entity name."""
        return self._name

    @property
    def should_poll(self):
        """No polling needed for a demo fan."""
        return False

    @property
    def current_direction(self) -> str:
        """Fan direction."""
        return self._direction

    @property
    def oscillating(self) -> bool:
        """Oscillating."""
        return self._oscillating

    @property
    def supported_features(self) -> int:
        """Flag supported features."""
        return self._supported_features


class AsyncDemoPercentageFan(BaseDemoFan, FanEntity):
    """An async demonstration fan component that uses percentages."""

    @property
    def percentage(self) -> str:
        """Return the current speed."""
        return self._percentage

    async def async_set_percentage(self, percentage: int) -> None:
        """Set the speed of the fan, as a percentage."""
        self._percentage = percentage
        self._preset_mode = None
        self.async_write_ha_state()

    @property
    def preset_mode(self) -> Optional[str]:
        """Return the current preset mode, e.g., auto, smart, interval, favorite."""
        return self._preset_mode

    @property
    def preset_modes(self) -> Optional[List[str]]:
        """Return a list of available preset modes."""
        return self._preset_modes

    async def async_set_preset_mode(self, preset_mode: str) -> None:
        """Set new preset mode."""
        if preset_mode not in self.preset_modes:
            raise ValueError(
                "{preset_mode} is not a valid preset_mode: {self.preset_modes}"
            )
        self._preset_mode = preset_mode
        self._percentage = None
        self.async_write_ha_state()

    async def async_turn_on(
        self,
        speed: str = None,
        percentage: int = None,
        preset_mode: str = None,
        **kwargs,
    ) -> None:
        """Turn on the entity."""
        if preset_mode:
            await self.async_set_preset_mode(preset_mode)
            return

        if percentage is None:
            percentage = 67

        await self.async_set_percentage(percentage)

    async def async_turn_off(self, **kwargs) -> None:
        """Turn off the entity."""
        await self.async_oscillate(False)
        await self.async_set_percentage(0)

    async def async_set_direction(self, direction: str) -> None:
        """Set the direction of the fan."""
        self._direction = direction
        self.async_write_ha_state()

    async def async_oscillate(self, oscillating: bool) -> None:
        """Set oscillation."""
        self._oscillating = oscillating
        self.async_write_ha_state()