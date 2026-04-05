"""Tests for M-TEC coordinator."""

from __future__ import annotations

from datetime import timedelta
from unittest.mock import AsyncMock

import pytest
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import UpdateFailed

from custom_components.mtec.api import MtecApiClient, MtecApiError
from custom_components.mtec.const import DOMAIN
from custom_components.mtec.coordinator import MtecDataCoordinator


async def test_coordinator_init(hass: HomeAssistant) -> None:
    """Test coordinator initialization."""
    client = AsyncMock(spec=MtecApiClient)
    coordinator = MtecDataCoordinator(hass, client, 30, {"firmware_version": "1.0.0"})

    assert coordinator.client == client
    assert coordinator.update_interval == timedelta(seconds=30)
    assert coordinator.device_info_data == {"firmware_version": "1.0.0"}
    assert coordinator.name == DOMAIN


async def test_coordinator_init_without_device_info(hass: HomeAssistant) -> None:
    """Test coordinator initialization without device info."""
    client = AsyncMock(spec=MtecApiClient)
    coordinator = MtecDataCoordinator(hass, client, 15)

    assert coordinator.device_info_data == {}


async def test_coordinator_update_success(hass: HomeAssistant) -> None:
    """Test successful data update."""
    client = AsyncMock(spec=MtecApiClient)
    client.async_read_values.return_value = {
        "outdoor_temp": 15.5,
        "heating_power": 3.5,
    }

    coordinator = MtecDataCoordinator(hass, client, 30)
    data = await coordinator._async_update_data()

    assert data["outdoor_temp"] == 15.5
    assert data["heating_power"] == 3.5
    client.async_read_values.assert_called_once()


async def test_coordinator_update_failure(hass: HomeAssistant) -> None:
    """Test data update with API error."""
    client = AsyncMock(spec=MtecApiClient)
    client.async_read_values.side_effect = MtecApiError("Connection failed")

    coordinator = MtecDataCoordinator(hass, client, 30)

    with pytest.raises(UpdateFailed, match="Error fetching data"):
        await coordinator._async_update_data()


async def test_coordinator_update_empty_data(hass: HomeAssistant) -> None:
    """Test data update with empty response."""
    client = AsyncMock(spec=MtecApiClient)
    client.async_read_values.return_value = {}

    coordinator = MtecDataCoordinator(hass, client, 30)
    data = await coordinator._async_update_data()

    assert data == {}


async def test_coordinator_last_update_success(hass: HomeAssistant) -> None:
    """Test last_update_success after failed then successful update."""
    client = AsyncMock(spec=MtecApiClient)

    coordinator = MtecDataCoordinator(hass, client, 30)

    # Simulate a failed update via the parent class refresh
    client.async_read_values.side_effect = MtecApiError("fail")
    await coordinator.async_refresh()
    assert coordinator.last_update_success is False

    # After successful update
    client.async_read_values.side_effect = None
    client.async_read_values.return_value = {"outdoor_temp": 15.5}
    await coordinator.async_refresh()
    assert coordinator.last_update_success is True
