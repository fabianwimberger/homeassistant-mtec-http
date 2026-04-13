"""Tests for M-TEC integration setup and teardown."""

from __future__ import annotations

from typing import Any
from unittest.mock import patch

from aioresponses import aioresponses
from homeassistant.config_entries import ConfigEntryState
from homeassistant.core import HomeAssistant

from custom_components.mtec.const import CONF_HOST, CONF_SCAN_INTERVAL, DOMAIN


async def test_setup_entry(hass: HomeAssistant) -> None:
    """Test successful setup of a config entry."""
    entry = _create_entry(hass)

    with _mock_setup():
        await hass.config_entries.async_setup(entry.entry_id)
        await hass.async_block_till_done()

    assert entry.state is ConfigEntryState.LOADED
    assert entry.runtime_data is not None


async def test_unload_entry(hass: HomeAssistant) -> None:
    """Test unloading a config entry."""
    entry = _create_entry(hass)

    with _mock_setup():
        await hass.config_entries.async_setup(entry.entry_id)
        await hass.async_block_till_done()

    assert entry.state is ConfigEntryState.LOADED

    await hass.config_entries.async_unload(entry.entry_id)
    await hass.async_block_till_done()

    assert entry.state is ConfigEntryState.NOT_LOADED


async def test_setup_entry_connection_failure(hass: HomeAssistant) -> None:
    """Test setup failure when probing fails."""
    entry = _create_entry(hass)

    with patch(
        "custom_components.mtec.api.MtecApiClient.async_probe_available_keys",
        side_effect=Exception("Connection refused"),
    ):
        await hass.config_entries.async_setup(entry.entry_id)
        await hass.async_block_till_done()

    assert entry.state is ConfigEntryState.SETUP_ERROR


async def test_setup_creates_entities(hass: HomeAssistant) -> None:
    """Test that setup creates sensor entities for available signals."""
    entry = _create_entry(hass)
    url = "http://192.168.1.100/var/readWriteVars"

    with aioresponses() as m:
        # Probe: each signal is requested individually; return 200 for outdoor_temp, 500 for rest
        def _probe_handler(url_: Any, **kwargs: Any) -> Any:
            import json

            from aioresponses import CallbackResult

            body = kwargs.get("json")
            if body is None:
                raw = kwargs.get("data")
                body = json.loads(raw) if raw else []
            name = body[0]["name"] if body else ""
            if "outdoorTemp" in name:
                return CallbackResult(
                    status=200, payload=[{"name": name, "value": "15.5"}]
                )
            if "applVersion" in name:
                return CallbackResult(
                    status=200, payload=[{"name": name, "value": "1.0.0"}]
                )
            if "systemSerialNumber" in name:
                return CallbackResult(
                    status=200, payload=[{"name": name, "value": "SN123"}]
                )
            return CallbackResult(status=500)

        # Register enough calls for probing + device info + first refresh
        for _ in range(200):
            m.post(url, callback=_probe_handler, repeat=False)

        await hass.config_entries.async_setup(entry.entry_id)
        await hass.async_block_till_done()

    assert entry.state is ConfigEntryState.LOADED

    # outdoor_temp should have produced a sensor entity
    entity = hass.states.get("sensor.m_tec_heat_pump_outdoor_temperature")
    assert entity is not None
    assert entity.state == "15.5"


async def test_setup_skips_unavailable_signals(hass: HomeAssistant) -> None:
    """Test that entities are not created for unavailable signals."""
    entry = _create_entry(hass)
    url = "http://192.168.1.100/var/readWriteVars"

    with aioresponses() as m:

        def _probe_handler(url_: Any, **kwargs: Any) -> Any:
            import json

            from aioresponses import CallbackResult

            body = kwargs.get("json")
            if body is None:
                raw = kwargs.get("data")
                body = json.loads(raw) if raw else []
            name = body[0]["name"] if body else ""
            if "outdoorTemp" in name:
                return CallbackResult(
                    status=200, payload=[{"name": name, "value": "15.5"}]
                )
            if "applVersion" in name:
                return CallbackResult(
                    status=200, payload=[{"name": name, "value": "1.0.0"}]
                )
            if "systemSerialNumber" in name:
                return CallbackResult(
                    status=200, payload=[{"name": name, "value": "SN123"}]
                )
            return CallbackResult(status=500)

        for _ in range(200):
            m.post(url, callback=_probe_handler, repeat=False)

        await hass.config_entries.async_setup(entry.entry_id)
        await hass.async_block_till_done()

    # heating_power was not available (returned 500), so no entity
    entity = hass.states.get("sensor.m_tec_heat_pump_heating_power")
    assert entity is None


def _create_entry(hass: HomeAssistant) -> Any:
    """Create and add a config entry using MockConfigEntry."""
    from pytest_homeassistant_custom_component.common import MockConfigEntry

    entry = MockConfigEntry(
        domain=DOMAIN,
        title="M-TEC (192.168.1.100)",
        data={CONF_HOST: "192.168.1.100", CONF_SCAN_INTERVAL: 30},
        unique_id="192.168.1.100",
    )
    entry.add_to_hass(hass)
    return entry


def _mock_setup() -> _CombinedPatches:
    """Return a context manager that mocks all external calls during setup."""
    return _CombinedPatches(
        patch(
            "custom_components.mtec.api.MtecApiClient.async_probe_available_keys",
            return_value={"outdoor_temp", "hc0_mode"},
        ),
        patch(
            "custom_components.mtec.api.MtecApiClient.async_read_device_info",
            return_value={"firmware_version": "1.0.0"},
        ),
        patch(
            "custom_components.mtec.coordinator.MtecDataCoordinator._async_update_data",
            return_value={"outdoor_temp": 15.5},
        ),
    )


class _CombinedPatches:  # noqa: N801
    """Combine multiple context managers."""

    def __init__(self, *patches: Any) -> None:
        self._patches = patches

    def __enter__(self) -> list[Any]:
        return [p.__enter__() for p in self._patches]

    def __exit__(self, *args: Any) -> None:
        for p in reversed(self._patches):
            p.__exit__(*args)
