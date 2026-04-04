"""Tests for M-TEC select platform."""
from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest

from custom_components.mtec.api import MtecApiError
from custom_components.mtec.const import SELECT_DESCRIPTIONS
from custom_components.mtec.select import MtecSelect


def test_select_current_option(coordinator_data):
    """Test select current option."""
    coordinator = MagicMock()
    coordinator.data = coordinator_data
    coordinator.last_update_success = True
    coordinator.client.host = "192.168.1.100"
    
    desc = next(d for d in SELECT_DESCRIPTIONS if d.key == "system_operating_mode")
    select = MtecSelect(coordinator, desc)
    
    # Mode 2 should map to "Auto Heat"
    assert select.current_option == "Auto Heat"


def test_select_current_option_none(coordinator_data):
    """Test select when data is None."""
    coordinator = MagicMock()
    coordinator.data = None
    coordinator.last_update_success = True
    coordinator.client.host = "192.168.1.100"
    
    desc = next(d for d in SELECT_DESCRIPTIONS if d.key == "system_operating_mode")
    select = MtecSelect(coordinator, desc)
    
    assert select.current_option is None


def test_select_options(coordinator_data):
    """Test select available options."""
    coordinator = MagicMock()
    coordinator.data = coordinator_data
    coordinator.last_update_success = True
    coordinator.client.host = "192.168.1.100"
    
    desc = next(d for d in SELECT_DESCRIPTIONS if d.key == "system_operating_mode")
    select = MtecSelect(coordinator, desc)
    
    assert "Standby" in select.options
    assert "Auto Heat" in select.options
    assert "Full Auto" in select.options


def test_select_unique_id(coordinator_data):
    """Test select unique ID."""
    coordinator = MagicMock()
    coordinator.data = coordinator_data
    coordinator.last_update_success = True
    coordinator.client.host = "192.168.1.100"
    
    desc = next(d for d in SELECT_DESCRIPTIONS if d.key == "hc0_mode")
    select = MtecSelect(coordinator, desc)
    
    assert select.unique_id == "192.168.1.100_hc0_mode_select"


async def test_select_option(coordinator_data):
    """Test selecting an option."""
    coordinator = MagicMock()
    coordinator.data = coordinator_data
    coordinator.last_update_success = True
    coordinator.client.host = "192.168.1.100"
    coordinator.async_request_refresh = AsyncMock()
    coordinator.client.async_write_value = AsyncMock()
    
    desc = next(d for d in SELECT_DESCRIPTIONS if d.key == "hc0_mode")
    select = MtecSelect(coordinator, desc)
    
    await select.async_select_option("Day")
    
    # "Day" should map to mode value 2
    coordinator.client.async_write_value.assert_called_once_with("hc0_mode", 2.0)
    coordinator.async_request_refresh.assert_called_once()


async def test_select_option_unknown(coordinator_data, caplog):
    """Test selecting an unknown option."""
    coordinator = MagicMock()
    coordinator.data = coordinator_data
    coordinator.last_update_success = True
    coordinator.client.host = "192.168.1.100"
    coordinator.async_request_refresh = AsyncMock()
    
    desc = next(d for d in SELECT_DESCRIPTIONS if d.key == "hc0_mode")
    select = MtecSelect(coordinator, desc)
    
    await select.async_select_option("UnknownMode")
    
    assert "Unknown option UnknownMode" in caplog.text
    coordinator.async_request_refresh.assert_not_called()


async def test_select_option_api_error(coordinator_data, caplog):
    """Test selecting option with API error."""
    coordinator = MagicMock()
    coordinator.data = coordinator_data
    coordinator.last_update_success = True
    coordinator.client.host = "192.168.1.100"
    coordinator.async_request_refresh = AsyncMock()
    coordinator.client.async_write_value = AsyncMock(
        side_effect=MtecApiError("Write failed")
    )
    
    desc = next(d for d in SELECT_DESCRIPTIONS if d.key == "hc0_mode")
    select = MtecSelect(coordinator, desc)
    
    await select.async_select_option("Night")
    
    assert "Failed to set hc0_mode" in caplog.text
    coordinator.async_request_refresh.assert_not_called()


def test_select_hot_water_mode(coordinator_data):
    """Test hot water mode select."""
    coordinator = MagicMock()
    coordinator.data = coordinator_data
    coordinator.last_update_success = True
    coordinator.client.host = "192.168.1.100"
    
    desc = next(d for d in SELECT_DESCRIPTIONS if d.key == "hot_water_mode")
    select = MtecSelect(coordinator, desc)
    
    # Mode 1 should map to "Time Program"
    assert select.current_option == "Time Program"
    assert "Off" in select.options
    assert "Continuous" in select.options


def test_select_sg_ready_mode(coordinator_data):
    """Test SG Ready mode select."""
    coordinator = MagicMock()
    coordinator.data = coordinator_data
    coordinator.last_update_success = True
    coordinator.client.host = "192.168.1.100"
    
    desc = next(d for d in SELECT_DESCRIPTIONS if d.key == "sg_ready_mode")
    select = MtecSelect(coordinator, desc)
    
    assert "Normal" in select.options
    assert "Force On" in select.options
