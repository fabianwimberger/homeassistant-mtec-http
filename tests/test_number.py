"""Tests for M-TEC number platform."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

from custom_components.mtec.api import MtecApiError
from custom_components.mtec.const import NUMBER_DESCRIPTIONS
from custom_components.mtec.number import MtecNumber


def test_number_native_value(coordinator_data):
    """Test number native value."""
    coordinator = MagicMock()
    coordinator.data = coordinator_data
    coordinator.last_update_success = True
    coordinator.client.host = "192.168.1.100"

    desc = next(d for d in NUMBER_DESCRIPTIONS if d.key == "hot_water_target_temp")
    number = MtecNumber(coordinator, desc)

    assert number.native_value == 48.0


def test_number_native_value_none(coordinator_data):
    """Test number when data is None."""
    coordinator = MagicMock()
    coordinator.data = None
    coordinator.last_update_success = True
    coordinator.client.host = "192.168.1.100"

    desc = next(d for d in NUMBER_DESCRIPTIONS if d.key == "hot_water_target_temp")
    number = MtecNumber(coordinator, desc)

    assert number.native_value is None


def test_number_unique_id(coordinator_data):
    """Test number unique ID."""
    coordinator = MagicMock()
    coordinator.data = coordinator_data
    coordinator.last_update_success = True
    coordinator.client.host = "192.168.1.100"

    desc = next(d for d in NUMBER_DESCRIPTIONS if d.key == "hc0_day_temp")
    number = MtecNumber(coordinator, desc)

    assert number.unique_id == "192.168.1.100_hc0_day_temp_number"


def test_number_limits(coordinator_data):
    """Test number min/max/step values."""
    coordinator = MagicMock()
    coordinator.data = coordinator_data
    coordinator.last_update_success = True
    coordinator.client.host = "192.168.1.100"

    desc = next(d for d in NUMBER_DESCRIPTIONS if d.key == "hc0_day_temp")
    number = MtecNumber(coordinator, desc)

    assert number.native_min_value == 10.0
    assert number.native_max_value == 30.0
    assert number.native_step == 0.5


async def test_number_set_value(coordinator_data):
    """Test setting number value."""
    coordinator = MagicMock()
    coordinator.data = coordinator_data
    coordinator.last_update_success = True
    coordinator.client.host = "192.168.1.100"
    coordinator.async_request_refresh = AsyncMock()

    desc = next(d for d in NUMBER_DESCRIPTIONS if d.key == "hc0_day_temp")
    number = MtecNumber(coordinator, desc)

    coordinator.client.async_write_value = AsyncMock()

    await number.async_set_native_value(22.5)

    coordinator.client.async_write_value.assert_called_once_with("hc0_day_temp", 22.5)
    coordinator.async_request_refresh.assert_called_once()


async def test_number_set_value_api_error(coordinator_data, caplog):
    """Test setting number value with API error."""
    coordinator = MagicMock()
    coordinator.data = coordinator_data
    coordinator.last_update_success = True
    coordinator.client.host = "192.168.1.100"
    coordinator.async_request_refresh = AsyncMock()

    desc = next(d for d in NUMBER_DESCRIPTIONS if d.key == "hc0_day_temp")
    number = MtecNumber(coordinator, desc)

    coordinator.client.async_write_value = AsyncMock(side_effect=MtecApiError("Write failed"))

    await number.async_set_native_value(22.5)

    assert "Failed to set hc0_day_temp" in caplog.text
    coordinator.async_request_refresh.assert_not_called()


def test_number_device_class(coordinator_data):
    """Test number device class."""
    coordinator = MagicMock()
    coordinator.data = coordinator_data
    coordinator.last_update_success = True
    coordinator.client.host = "192.168.1.100"

    desc = next(d for d in NUMBER_DESCRIPTIONS if d.key == "hot_water_target_temp")
    number = MtecNumber(coordinator, desc)

    assert number.device_class is not None
