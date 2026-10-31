"""Fixtures for the Xiaomi Smart Air Purifier 4 Compact tests."""
from __future__ import annotations

from typing import Any
from unittest.mock import MagicMock, patch

import pytest
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.xiaomi_air_purifier_4_compact.api import PurifierInfo
from custom_components.xiaomi_air_purifier_4_compact.const import DOMAIN

HOST = "192.0.2.10"
TOKEN = "0123456789abcdef0123456789abcdef"
MAC = "AA:BB:CC:DD:EE:FF"

# Values read from a real cpa4 (firmware 2.2.10_0021).
STATUS: dict[str, Any] = {
    "on": True,
    "fault": 0,
    "mode": 0,
    "pm25": 11,
    "filter_life": 95,
    "filter_used_time": 352,
    "filter_left_time": 277,
    "alarm": False,
    "child_lock": True,
    "motor_speed": 420,
    "favorite_level": 7,
    "brightness": 0,
}


@pytest.fixture(autouse=True)
def auto_enable_custom_integrations(enable_custom_integrations):
    """Load custom_components/ in every test."""
    yield


@pytest.fixture
def mock_client():
    """A fake XiaomiAirPurifier, patched in both the coordinator and the config flow."""
    client = MagicMock()
    client.info.return_value = PurifierInfo("xiaomi.airp.cpa4", MAC, "2.2.10_0021", "esp32")
    client.status.return_value = dict(STATUS)
    with (
        patch(
            "custom_components.xiaomi_air_purifier_4_compact.coordinator.XiaomiAirPurifier",
            return_value=client,
        ),
        patch(
            "custom_components.xiaomi_air_purifier_4_compact.config_flow.XiaomiAirPurifier",
            return_value=client,
        ),
    ):
        yield client


@pytest.fixture
def config_entry() -> MockConfigEntry:
    return MockConfigEntry(
        domain=DOMAIN,
        unique_id="aa:bb:cc:dd:ee:ff",
        data={
            "host": HOST,
            "token": TOKEN,
            "name": "Purifier",
            "mac": MAC,
            "model": "xiaomi.airp.cpa4",
        },
    )
