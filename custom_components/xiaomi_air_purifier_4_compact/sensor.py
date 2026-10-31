"""Sensor platform for Xiaomi Smart Air Purifier 4 Compact."""
from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    CONCENTRATION_MICROGRAMS_PER_CUBIC_METER,
    PERCENTAGE,
    REVOLUTIONS_PER_MINUTE,
    EntityCategory,
    UnitOfTime,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN, FAULT_TO_STATE, Prop
from .coordinator import XiaomiAirPurifierCoordinator
from .entity import XiaomiAirPurifierEntity


@dataclass(frozen=True, kw_only=True)
class XiaomiAirPurifierSensorDescription(SensorEntityDescription):
    """Sensor bound to a polled property, with an optional value mapping."""

    value_fn: Callable[[Any], Any] = lambda value: value


SENSORS: tuple[XiaomiAirPurifierSensorDescription, ...] = (
    XiaomiAirPurifierSensorDescription(
        key=Prop.PM25,
        device_class=SensorDeviceClass.PM25,
        native_unit_of_measurement=CONCENTRATION_MICROGRAMS_PER_CUBIC_METER,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    XiaomiAirPurifierSensorDescription(
        key=Prop.FILTER_LIFE,
        translation_key="filter_life",
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:air-filter",
    ),
    XiaomiAirPurifierSensorDescription(
        key=Prop.FILTER_LEFT_TIME,
        translation_key="filter_left_time",
        device_class=SensorDeviceClass.DURATION,
        native_unit_of_measurement=UnitOfTime.DAYS,
        icon="mdi:air-filter",
    ),
    XiaomiAirPurifierSensorDescription(
        key=Prop.FILTER_USED_TIME,
        translation_key="filter_used_time",
        device_class=SensorDeviceClass.DURATION,
        native_unit_of_measurement=UnitOfTime.HOURS,
        state_class=SensorStateClass.TOTAL_INCREASING,
        entity_category=EntityCategory.DIAGNOSTIC,
        icon="mdi:clock-outline",
    ),
    XiaomiAirPurifierSensorDescription(
        key=Prop.MOTOR_SPEED,
        translation_key="motor_speed",
        native_unit_of_measurement=REVOLUTIONS_PER_MINUTE,
        state_class=SensorStateClass.MEASUREMENT,
        entity_category=EntityCategory.DIAGNOSTIC,
        icon="mdi:fan",
    ),
    XiaomiAirPurifierSensorDescription(
        key=Prop.FAULT,
        translation_key="fault",
        device_class=SensorDeviceClass.ENUM,
        options=list(FAULT_TO_STATE.values()),
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=FAULT_TO_STATE.get,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Xiaomi Air Purifier sensors."""
    coordinator: XiaomiAirPurifierCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        XiaomiAirPurifierSensor(coordinator, entry, description) for description in SENSORS
    )


class XiaomiAirPurifierSensor(XiaomiAirPurifierEntity, SensorEntity):
    """A read-only property of the purifier."""

    entity_description: XiaomiAirPurifierSensorDescription

    def __init__(
        self,
        coordinator: XiaomiAirPurifierCoordinator,
        entry: ConfigEntry,
        description: XiaomiAirPurifierSensorDescription,
    ) -> None:
        super().__init__(coordinator, entry, description.key)
        self.entity_description = description

    @property
    def native_value(self) -> Any:
        return self.entity_description.value_fn(self._value)
