"""Set up the integration in Home Assistant against the real device.

Writes are no-ops: each value written is the one just read back.
"""
import os

from homeassistant.config_entries import ConfigEntryState
from homeassistant.helpers import entity_registry as er
import pytest
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.xiaomi_air_purifier_4_compact.const import DOMAIN

HOST = os.environ.get("PURIFIER_HOST")
TOKEN = os.environ.get("PURIFIER_TOKEN")

pytestmark = [
    pytest.mark.skipif(not HOST or not TOKEN, reason="PURIFIER_HOST/PURIFIER_TOKEN not set"),
    pytest.mark.enable_socket,
]


@pytest.fixture
def expected_lingering_timers() -> bool:
    return True


async def test_live(hass, socket_enabled) -> None:
    result = await hass.config_entries.flow.async_init(DOMAIN, context={"source": "user"})
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], {"host": HOST, "token": TOKEN, "name": "Live"}
    )
    assert result["type"] == "create_entry", result
    entry = result["result"]
    await hass.async_block_till_done()
    assert entry.state is ConfigEntryState.LOADED

    entities = er.async_entries_for_config_entry(er.async_get(hass), entry.entry_id)
    for ent in sorted(entities, key=lambda e: e.entity_id):
        state = hass.states.get(ent.entity_id)
        print(f"{ent.entity_id:55} {state.state:12} {dict(state.attributes).get('preset_mode', '')}")
        assert state.state != "unavailable", ent.entity_id

    coordinator = hass.data[DOMAIN][entry.entry_id]
    data = dict(coordinator.data)
    await coordinator.async_set_child_lock(data["child_lock"])
    await coordinator.async_set_alarm(data["alarm"])
    await coordinator.async_set_favorite_level(data["favorite_level"])
    await coordinator.async_set_mode({0: "auto", 1: "sleep", 2: "favorite"}[data["mode"]])
    await coordinator.async_refresh()
    changed = {k: (v, coordinator.data.get(k)) for k, v in data.items()
               if k in ("child_lock", "alarm", "favorite_level", "mode") and coordinator.data.get(k) != v}
    print("no-op writes ok, changed:", changed)
    assert not changed

    assert await hass.config_entries.async_unload(entry.entry_id)
