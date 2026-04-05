"""Tests for M-TEC integration setup and teardown."""

from __future__ import annotations

from typing import Any
from unittest.mock import patch

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
