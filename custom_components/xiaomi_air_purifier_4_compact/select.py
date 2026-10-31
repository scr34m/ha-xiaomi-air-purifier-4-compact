"""Select platform for Xiaomi Smart Air Purifier 4 Compact."""
from __future__ import annotations

from typing import Optional

from homeassistant.components.select import SelectEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import (
    BRIGHTNESS_TO_INT,
    DOMAIN,
    INT_TO_BRIGHTNESS,
    INT_TO_MODE,
    MODE_TO_INT,
    Prop,
)
from .coordinator import XiaomiAirPurifierCoordinator
from .entity import XiaomiAirPurifierEntity


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Xiaomi Air Purifier select entities."""
    coordinator: XiaomiAirPurifierCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        [
            XiaomiAirPurifierModeSelect(coordinator, entry),
            XiaomiAirPurifierBrightnessSelect(coordinator, entry),
        ]
    )


class XiaomiAirPurifierModeSelect(XiaomiAirPurifierEntity, SelectEntity):
    """Operating mode ('auto', 'sleep', 'favorite'), same as the fan preset."""

    _attr_translation_key = "mode"
    _attr_options = list(MODE_TO_INT)
    _attr_icon = "mdi:air-purifier"

    def __init__(self, coordinator: XiaomiAirPurifierCoordinator, entry: ConfigEntry) -> None:
        super().__init__(coordinator, entry, Prop.MODE)

    @property
    def current_option(self) -> Optional[str]:
        return INT_TO_MODE.get(self._value)

    async def async_select_option(self, option: str) -> None:
        await self.coordinator.async_set_mode(option)


class XiaomiAirPurifierBrightnessSelect(XiaomiAirPurifierEntity, SelectEntity):
    """Screen brightness ('off', 'dim', 'bright')."""

    _attr_translation_key = "brightness"
    _attr_options = list(BRIGHTNESS_TO_INT)
    _attr_entity_category = EntityCategory.CONFIG
    _attr_icon = "mdi:brightness-6"

    def __init__(self, coordinator: XiaomiAirPurifierCoordinator, entry: ConfigEntry) -> None:
        super().__init__(coordinator, entry, Prop.BRIGHTNESS)

    @property
    def current_option(self) -> Optional[str]:
        return INT_TO_BRIGHTNESS.get(self._value)

    async def async_select_option(self, option: str) -> None:
        await self.coordinator.async_set_brightness(option)
