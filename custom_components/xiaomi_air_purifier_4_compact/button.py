"""Button platform for Xiaomi Smart Air Purifier 4 Compact."""
from __future__ import annotations

from homeassistant.components.button import ButtonEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN, Prop
from .coordinator import XiaomiAirPurifierCoordinator
from .entity import XiaomiAirPurifierEntity


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Xiaomi Air Purifier buttons."""
    coordinator: XiaomiAirPurifierCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([XiaomiAirPurifierResetFilterButton(coordinator, entry)])


class XiaomiAirPurifierResetFilterButton(XiaomiAirPurifierEntity, ButtonEntity):
    """Reset the filter life after a filter change."""

    _attr_translation_key = "reset_filter"
    _attr_entity_category = EntityCategory.CONFIG
    _attr_icon = "mdi:air-filter"

    def __init__(self, coordinator: XiaomiAirPurifierCoordinator, entry: ConfigEntry) -> None:
        # Bound to the filter life so that it follows the device availability.
        super().__init__(coordinator, entry, Prop.FILTER_LIFE)
        self._attr_unique_id = f"{entry.entry_id}_reset_filter"

    async def async_press(self) -> None:
        await self.coordinator.async_reset_filter()
