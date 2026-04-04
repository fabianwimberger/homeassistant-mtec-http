"""Tests for M-TEC diagnostics."""
from __future__ import annotations

from datetime import timedelta
from unittest.mock import MagicMock

import pytest

from custom_components.mtec.const import CONF_HOST
from custom_components.mtec.diagnostics import async_get_config_entry_diagnostics


async def test_diagnostics(hass):
    """Test diagnostics output."""
    entry = MagicMock()
    entry.data = {CONF_HOST: "192.168.1.100"}
    
    coordinator = MagicMock()
    coordinator.update_interval = timedelta(seconds=30)
    coordinator.last_update_success = True
    coordinator.data = {
        "outdoor_temp": 15.5,
        "heating_power": 3.5,
    }
    
    entry.runtime_data = coordinator
    
    result = await async_get_config_entry_diagnostics(hass, entry)
    
    assert result["config"]["host"] == "192.168.1.100"
    assert result["config"]["scan_interval"] == 30
    assert result["last_update_success"] is True
    assert result["data"]["outdoor_temp"] == 15.5
    assert result["data"]["heating_power"] == 3.5


async def test_diagnostics_no_data(hass):
    """Test diagnostics when no data available."""
    entry = MagicMock()
    entry.data = {CONF_HOST: "192.168.1.100"}
    
    coordinator = MagicMock()
    coordinator.update_interval = timedelta(seconds=15)
    coordinator.last_update_success = False
    coordinator.data = None
    
    entry.runtime_data = coordinator
    
    result = await async_get_config_entry_diagnostics(hass, entry)
    
    assert result["config"]["host"] == "192.168.1.100"
    assert result["config"]["scan_interval"] == 15
    assert result["last_update_success"] is False
    assert result["data"] == {}


async def test_diagnostics_no_interval(hass):
    """Test diagnostics when update_interval is None."""
    entry = MagicMock()
    entry.data = {CONF_HOST: "192.168.1.100"}
    
    coordinator = MagicMock()
    coordinator.update_interval = None
    coordinator.last_update_success = True
    coordinator.data = {"outdoor_temp": 20.0}
    
    entry.runtime_data = coordinator
    
    result = await async_get_config_entry_diagnostics(hass, entry)
    
    assert result["config"]["scan_interval"] is None
