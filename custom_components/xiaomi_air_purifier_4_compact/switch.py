"""Switch platform for Xiaomi Smart Air Purifier 4 Compact."""
from __future__ import annotations

from typing import Any, Optional

from homeassistant.components.switch import SwitchEntity
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
    """Set up Xiaomi Air Purifier switches."""
    coordinator: XiaomiAirPurifierCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        [
            XiaomiAirPurifierChildLockSwitch(coordinator, entry),
            XiaomiAirPurifierAlarmSwitch(coordinator, entry),
        ]
    )


class XiaomiAirPurifierChildLockSwitch(XiaomiAirPurifierEntity, SwitchEntity):
    """Physical button lock."""

    _attr_translation_key = "child_lock"
    _attr_entity_category = EntityCategory.CONFIG
    _attr_icon = "mdi:lock"

    def __init__(self, coordinator: XiaomiAirPurifierCoordinator, entry: ConfigEntry) -> None:
        super().__init__(coordinator, entry, Prop.CHILD_LOCK)

    @property
    def is_on(self) -> Optional[bool]:
        return self._value

    async def async_turn_on(self, **kwargs: Any) -> None:
        await self.coordinator.async_set_child_lock(True)

    async def async_turn_off(self, **kwargs: Any) -> None:
        await self.coordinator.async_set_child_lock(False)


class XiaomiAirPurifierAlarmSwitch(XiaomiAirPurifierEntity, SwitchEntity):
    """Button beep."""

    _attr_translation_key = "alarm"
    _attr_entity_category = EntityCategory.CONFIG
    _attr_icon = "mdi:volume-high"

    def __init__(self, coordinator: XiaomiAirPurifierCoordinator, entry: ConfigEntry) -> None:
        super().__init__(coordinator, entry, Prop.ALARM)

    @property
    def is_on(self) -> Optional[bool]:
        return self._value

    async def async_turn_on(self, **kwargs: Any) -> None:
        await self.coordinator.async_set_alarm(True)

    async def async_turn_off(self, **kwargs: Any) -> None:
        await self.coordinator.async_set_alarm(False)
