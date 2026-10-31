"""Number platform for Xiaomi Smart Air Purifier 4 Compact."""
from __future__ import annotations

from typing import Optional

from homeassistant.components.number import NumberEntity, NumberMode
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN, FAVORITE_LEVEL_MAX, FAVORITE_LEVEL_MIN, Prop
from .coordinator import XiaomiAirPurifierCoordinator
from .entity import XiaomiAirPurifierEntity


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Xiaomi Air Purifier number entities."""
    coordinator: XiaomiAirPurifierCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([XiaomiAirPurifierFavoriteLevelNumber(coordinator, entry)])


class XiaomiAirPurifierFavoriteLevelNumber(XiaomiAirPurifierEntity, NumberEntity):
    """Fan level used in Favorite mode (0-14)."""

    _attr_translation_key = "favorite_level"
    _attr_entity_category = EntityCategory.CONFIG
    _attr_native_min_value = FAVORITE_LEVEL_MIN
    _attr_native_max_value = FAVORITE_LEVEL_MAX
    _attr_native_step = 1
    _attr_mode = NumberMode.SLIDER
    _attr_icon = "mdi:fan-speed-3"

    def __init__(self, coordinator: XiaomiAirPurifierCoordinator, entry: ConfigEntry) -> None:
        super().__init__(coordinator, entry, Prop.FAVORITE_LEVEL)

    @property
    def native_value(self) -> Optional[float]:
        return self._value

    async def async_set_native_value(self, value: float) -> None:
        await self.coordinator.async_set_favorite_level(int(value))
