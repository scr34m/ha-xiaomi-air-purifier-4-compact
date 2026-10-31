"""Fan platform for Xiaomi Smart Air Purifier 4 Compact."""
from __future__ import annotations

from typing import Any, Optional

from homeassistant.components.fan import FanEntity, FanEntityFeature
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.util.percentage import (
    percentage_to_ranged_value,
    ranged_value_to_percentage,
)

from .const import (
    DOMAIN,
    FAVORITE_LEVEL_MAX,
    INT_TO_MODE,
    MODE_FAVORITE,
    MODE_TO_INT,
    Prop,
)
from .coordinator import XiaomiAirPurifierCoordinator
from .entity import XiaomiAirPurifierEntity

# Percentage 1-100 maps to favorite level 1-14; level 0 is reachable through
# the Favorite Level number entity.
SPEED_RANGE = (1, FAVORITE_LEVEL_MAX)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Xiaomi Air Purifier fan."""
    coordinator: XiaomiAirPurifierCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([XiaomiAirPurifierFan(coordinator, entry)])


class XiaomiAirPurifierFan(XiaomiAirPurifierEntity, FanEntity):
    """The purifier: power, preset mode and favorite speed."""

    _attr_name = None
    _attr_translation_key = "air_purifier"
    _attr_preset_modes = list(MODE_TO_INT)
    _attr_speed_count = SPEED_RANGE[1] - SPEED_RANGE[0] + 1
    _attr_supported_features = (
        FanEntityFeature.TURN_ON
        | FanEntityFeature.TURN_OFF
        | FanEntityFeature.PRESET_MODE
        | FanEntityFeature.SET_SPEED
    )

    def __init__(self, coordinator: XiaomiAirPurifierCoordinator, entry: ConfigEntry) -> None:
        super().__init__(coordinator, entry, Prop.ON)

    @property
    def is_on(self) -> Optional[bool]:
        return self._value

    @property
    def preset_mode(self) -> Optional[str]:
        return INT_TO_MODE.get((self.coordinator.data or {}).get(Prop.MODE))

    @property
    def percentage(self) -> Optional[int]:
        """Favorite level as a percentage, only meaningful in Favorite mode."""
        if not self.is_on or self.preset_mode != MODE_FAVORITE:
            return None
        level = (self.coordinator.data or {}).get(Prop.FAVORITE_LEVEL)
        if level is None:
            return None
        return ranged_value_to_percentage(SPEED_RANGE, max(level, SPEED_RANGE[0]))

    async def async_turn_on(
        self,
        percentage: Optional[int] = None,
        preset_mode: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        if not self.is_on:
            await self.coordinator.async_set_power(True)
        if preset_mode is not None:
            await self.async_set_preset_mode(preset_mode)
        elif percentage is not None:
            await self.async_set_percentage(percentage)

    async def async_turn_off(self, **kwargs: Any) -> None:
        await self.coordinator.async_set_power(False)

    async def async_set_preset_mode(self, preset_mode: str) -> None:
        await self.coordinator.async_set_mode(preset_mode)

    async def async_set_percentage(self, percentage: int) -> None:
        """Speed means Favorite mode at the matching favorite level."""
        if percentage == 0:
            await self.async_turn_off()
            return
        level = round(percentage_to_ranged_value(SPEED_RANGE, percentage))
        if not self.is_on:
            await self.coordinator.async_set_power(True)
        await self.coordinator.async_set_favorite_level(level)
        if self.preset_mode != MODE_FAVORITE:
            await self.coordinator.async_set_mode(MODE_FAVORITE)
