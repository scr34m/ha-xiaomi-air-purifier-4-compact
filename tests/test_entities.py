"""Entity tests: states from the polled values and the writes they send."""
from __future__ import annotations

from homeassistant.config_entries import ConfigEntryState
from homeassistant.helpers import entity_registry as er
import pytest

from custom_components.xiaomi_air_purifier_4_compact.api import PurifierConnectionError


@pytest.fixture
async def setup(hass, mock_client, config_entry):
    config_entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(config_entry.entry_id)
    await hass.async_block_till_done()
    return config_entry


def _entity_id(hass, platform: str, key: str) -> str:
    entry_id = hass.config_entries.async_entries("xiaomi_air_purifier_4_compact")[0].entry_id
    entity_id = er.async_get(hass).async_get_entity_id(
        platform, "xiaomi_air_purifier_4_compact", f"{entry_id}_{key}"
    )
    assert entity_id, (platform, key)
    return entity_id


async def test_states(hass, setup) -> None:
    assert setup.state is ConfigEntryState.LOADED
    fan = hass.states.get(_entity_id(hass, "fan", "on"))
    assert fan.state == "on"
    assert fan.attributes["preset_mode"] == "auto"
    assert fan.attributes["percentage"] is None
    assert hass.states.get(_entity_id(hass, "sensor", "pm25")).state == "11"
    assert hass.states.get(_entity_id(hass, "sensor", "filter_life")).state == "95"
    assert hass.states.get(_entity_id(hass, "sensor", "filter_left_time")).state == "277"
    assert hass.states.get(_entity_id(hass, "sensor", "motor_speed")).state == "420"
    assert hass.states.get(_entity_id(hass, "sensor", "fault")).state == "no_fault"
    assert hass.states.get(_entity_id(hass, "switch", "child_lock")).state == "on"
    assert hass.states.get(_entity_id(hass, "switch", "alarm")).state == "off"
    assert hass.states.get(_entity_id(hass, "number", "favorite_level")).state == "7"
    assert hass.states.get(_entity_id(hass, "select", "mode")).state == "auto"
    assert hass.states.get(_entity_id(hass, "select", "brightness")).state == "off"


async def test_fan_turn_off(hass, setup, mock_client) -> None:
    await hass.services.async_call(
        "fan", "turn_off", {"entity_id": _entity_id(hass, "fan", "on")}, blocking=True
    )
    mock_client.set_property.assert_called_with(2, 1, False)


async def test_fan_preset(hass, setup, mock_client) -> None:
    await hass.services.async_call(
        "fan",
        "set_preset_mode",
        {"entity_id": _entity_id(hass, "fan", "on"), "preset_mode": "sleep"},
        blocking=True,
    )
    mock_client.set_property.assert_called_with(2, 4, 1)


async def test_fan_percentage_sets_favorite(hass, setup, mock_client) -> None:
    await hass.services.async_call(
        "fan",
        "set_percentage",
        {"entity_id": _entity_id(hass, "fan", "on"), "percentage": 100},
        blocking=True,
    )
    calls = [c.args for c in mock_client.set_property.call_args_list]
    assert calls == [(9, 11, 14), (2, 4, 2)]


async def test_number_select_switch_button(hass, setup, mock_client) -> None:
    await hass.services.async_call(
        "number",
        "set_value",
        {"entity_id": _entity_id(hass, "number", "favorite_level"), "value": 3},
        blocking=True,
    )
    mock_client.set_property.assert_called_with(9, 11, 3)
    await hass.services.async_call(
        "select",
        "select_option",
        {"entity_id": _entity_id(hass, "select", "brightness"), "option": "bright"},
        blocking=True,
    )
    mock_client.set_property.assert_called_with(13, 2, 2)
    await hass.services.async_call(
        "switch", "turn_off", {"entity_id": _entity_id(hass, "switch", "child_lock")}, blocking=True
    )
    mock_client.set_property.assert_called_with(8, 1, False)
    await hass.services.async_call(
        "button", "press", {"entity_id": _entity_id(hass, "button", "reset_filter")}, blocking=True
    )
    mock_client.call_action.assert_called_with(4, 1)


async def test_offline_at_startup(hass, mock_client, config_entry) -> None:
    mock_client.status.side_effect = PurifierConnectionError("timeout")
    config_entry.add_to_hass(hass)
    await hass.config_entries.async_setup(config_entry.entry_id)
    assert config_entry.state is ConfigEntryState.SETUP_RETRY


async def test_unload(hass, setup) -> None:
    assert await hass.config_entries.async_unload(setup.entry_id)
    assert setup.state is ConfigEntryState.NOT_LOADED
