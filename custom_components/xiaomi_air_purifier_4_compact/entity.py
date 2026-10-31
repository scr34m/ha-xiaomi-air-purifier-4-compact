"""Base entity for Xiaomi Smart Air Purifier 4 Compact."""
from __future__ import annotations

from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.device_registry import CONNECTION_NETWORK_MAC, DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import CONF_MAC, CONF_MODEL, DEFAULT_MODEL, DOMAIN
from .coordinator import XiaomiAirPurifierCoordinator


class XiaomiAirPurifierEntity(CoordinatorEntity[XiaomiAirPurifierCoordinator]):
    """Entity bound to one polled property of the purifier."""

    _attr_has_entity_name = True

    def __init__(
        self, coordinator: XiaomiAirPurifierCoordinator, entry: ConfigEntry, key: str
    ) -> None:
        """Initialize the entity."""
        super().__init__(coordinator)
        self.entry = entry
        self._key = key
        self._attr_unique_id = f"{entry.entry_id}_{key}"
        mac = entry.data.get(CONF_MAC)
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            connections={(CONNECTION_NETWORK_MAC, mac)} if mac else set(),
            name=coordinator.device_name,
            manufacturer="Xiaomi",
            model=entry.data.get(CONF_MODEL, DEFAULT_MODEL),
        )

    @property
    def _value(self) -> Any:
        if self.coordinator.data is None:
            return None
        return self.coordinator.data.get(self._key)

    @property
    def available(self) -> bool:
        """Unavailable when the last poll failed or did not return the property."""
        return super().available and self._value is not None
