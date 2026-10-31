"""DataUpdateCoordinator for the Xiaomi Smart Air Purifier 4 Compact."""
from __future__ import annotations

import asyncio
from datetime import timedelta
import logging
from typing import Any, Callable, TypeVar

from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import PurifierError, XiaomiAirPurifier
from .const import (
    BRIGHTNESS_TO_INT,
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
    FAVORITE_LEVEL_MAX,
    FAVORITE_LEVEL_MIN,
    MODE_TO_INT,
    POLLED_PROPERTIES,
    Prop,
    PurifierAIID,
    PurifierSIID,
)

_LOGGER = logging.getLogger(__name__)

_T = TypeVar("_T")


class XiaomiAirPurifierCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Polls the purifier and sends its commands, one request at a time."""

    def __init__(
        self,
        hass: HomeAssistant,
        ip: str,
        token: str,
        name: str,
        entry_id: str,
    ) -> None:
        """Initialize coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name=f"{DOMAIN}_{ip}",
            update_interval=timedelta(seconds=DEFAULT_SCAN_INTERVAL),
        )
        self.ip = ip
        self.device_name = name
        self.entry_id = entry_id
        self.client = XiaomiAirPurifier(ip, token)
        self._lock = asyncio.Lock()

    async def _async_run(self, func: Callable[..., _T], *args: Any) -> _T:
        async with self._lock:
            return await self.hass.async_add_executor_job(func, *args)

    async def _async_update_data(self) -> dict[str, Any]:
        """Fetch all polled properties from the purifier."""
        try:
            values = await self._async_run(self.client.status)
        except PurifierError as err:
            raise UpdateFailed(f"Error communicating with Xiaomi Air Purifier: {err}") from err
        if not values:
            raise UpdateFailed("Xiaomi Air Purifier returned no properties")
        return values

    # --------------------------------------------------------------------------
    # Control Actions
    # --------------------------------------------------------------------------
    async def _async_write(self, key: str, value: Any) -> None:
        """Write a polled property and show the new value right away."""
        siid, piid = POLLED_PROPERTIES[key]
        try:
            await self._async_run(self.client.set_property, siid, piid, value)
        except PurifierError as err:
            raise HomeAssistantError(f"Could not set {key}: {err}") from err
        if self.data is not None:
            self.async_set_updated_data({**self.data, key: value})
        await self.async_request_refresh()

    async def async_set_power(self, on: bool) -> None:
        """Turn the purifier on or off."""
        await self._async_write(Prop.ON, on)

    async def async_set_mode(self, mode: str) -> None:
        """Set 'auto', 'sleep' or 'favorite'."""
        await self._async_write(Prop.MODE, MODE_TO_INT[mode])

    async def async_set_favorite_level(self, level: int) -> None:
        """Set the fan level used in Favorite mode (0-14)."""
        level = max(FAVORITE_LEVEL_MIN, min(FAVORITE_LEVEL_MAX, int(level)))
        await self._async_write(Prop.FAVORITE_LEVEL, level)

    async def async_set_child_lock(self, locked: bool) -> None:
        """Lock or unlock the physical button."""
        await self._async_write(Prop.CHILD_LOCK, locked)

    async def async_set_alarm(self, enabled: bool) -> None:
        """Enable or disable the button beep."""
        await self._async_write(Prop.ALARM, enabled)

    async def async_set_brightness(self, brightness: str) -> None:
        """Set screen brightness ('off', 'dim', 'bright')."""
        await self._async_write(Prop.BRIGHTNESS, BRIGHTNESS_TO_INT[brightness])

    async def async_reset_filter(self) -> None:
        """Reset the filter life after a filter change."""
        try:
            await self._async_run(
                self.client.call_action, PurifierSIID.FILTER, PurifierAIID.RESET_FILTER_LIFE
            )
        except PurifierError as err:
            raise HomeAssistantError(f"Could not reset filter: {err}") from err
        await self.async_request_refresh()
