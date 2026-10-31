"""Config flow tests."""
from __future__ import annotations

from homeassistant import config_entries
from homeassistant.data_entry_flow import FlowResultType

from custom_components.xiaomi_air_purifier_4_compact.api import (
    PurifierConnectionError,
    PurifierInfo,
)
from custom_components.xiaomi_air_purifier_4_compact.const import DOMAIN

from .conftest import HOST, MAC, TOKEN


async def _start(hass, user_input):
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    return await hass.config_entries.flow.async_configure(result["flow_id"], user_input)


async def test_create_entry(hass, mock_client) -> None:
    result = await _start(hass, {"host": HOST, "token": TOKEN.upper(), "name": "Purifier"})
    assert result["type"] is FlowResultType.CREATE_ENTRY
    assert result["data"]["token"] == TOKEN
    assert result["data"]["mac"] == MAC
    assert result["result"].unique_id == "aa:bb:cc:dd:ee:ff"


async def test_invalid_token(hass, mock_client) -> None:
    result = await _start(hass, {"host": HOST, "token": "abc", "name": "Purifier"})
    assert result["errors"] == {"token": "invalid_token"}
    mock_client.info.assert_not_called()


async def test_cannot_connect(hass, mock_client) -> None:
    mock_client.info.side_effect = PurifierConnectionError("timeout")
    result = await _start(hass, {"host": HOST, "token": TOKEN, "name": "Purifier"})
    assert result["errors"] == {"base": "cannot_connect"}


async def test_unsupported_model(hass, mock_client) -> None:
    mock_client.info.return_value = PurifierInfo("xiaomi.feeder.iv2001", MAC, None, None)
    result = await _start(hass, {"host": HOST, "token": TOKEN, "name": "Purifier"})
    assert result["errors"] == {"base": "unsupported_model"}


async def test_already_configured_updates_host(hass, mock_client, config_entry) -> None:
    config_entry.add_to_hass(hass)
    result = await _start(hass, {"host": "192.0.2.20", "token": TOKEN, "name": "Purifier"})
    assert result["type"] is FlowResultType.ABORT
    assert result["reason"] == "already_configured"
    assert config_entry.data["host"] == "192.0.2.20"
