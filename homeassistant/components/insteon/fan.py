"""Support for INSTEON fans via PowerLinc Modem."""
import math

from homeassistant.components.fan import (
    DOMAIN as FAN_DOMAIN,
    SUPPORT_SET_SPEED,
    FanEntity,
)
from homeassistant.core import callback
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.util.percentage import (
    percentage_to_ranged_value,
    ranged_value_to_percentage,
)

from .const import SIGNAL_ADD_ENTITIES
from .insteon_entity import InsteonEntity
from .utils import async_add_insteon_entities

SPEED_RANGE = (0x00, 0xFF)  # off is not included


async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up the Insteon fans from a config entry."""

    @callback
    def async_add_insteon_fan_entities(discovery_info=None):
        """Add the Insteon entities for the platform."""
        async_add_insteon_entities(
            hass, FAN_DOMAIN, InsteonFanEntity, async_add_entities, discovery_info
        )

    signal = f"{SIGNAL_ADD_ENTITIES}_{FAN_DOMAIN}"
    async_dispatcher_connect(hass, signal, async_add_insteon_fan_entities)
    async_add_insteon_fan_entities()


class InsteonFanEntity(InsteonEntity, FanEntity):
    """An INSTEON fan entity."""

    @property
    def percentage(self) -> str:
        """Return the current speed percentage."""
        if self._insteon_device_group.value is None:
            return None
        return ranged_value_to_percentage(SPEED_RANGE, self._insteon_device_group.value)

    @property
    def supported_features(self) -> int:
        """Flag supported features."""
        return SUPPORT_SET_SPEED

    @property
    def speed_count(self) -> int:
        """Flag supported features."""
        return 3

    async def async_turn_on(
        self,
        speed: str = None,
        percentage: int = None,
        preset_mode: str = None,
        **kwargs,
    ) -> None:
        """Turn on the fan."""
        await self.async_set_percentage(percentage or 67)

    async def async_turn_off(self, **kwargs) -> None:
        """Turn off the fan."""
        await self._insteon_device.async_fan_off()

    async def async_set_percentage(self, percentage: int) -> None:
        """Set the speed percentage of the fan."""
        if percentage == 0:
            await self.async_turn_off()
            return
        on_level = math.ceil(percentage_to_ranged_value(SPEED_RANGE, percentage))
        await self._insteon_device.async_on(group=2, on_level=on_level)
