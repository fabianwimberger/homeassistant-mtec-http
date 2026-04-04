"""Tests for M-TEC climate platform."""
from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest
from homeassistant.components.climate import HVACMode

from custom_components.mtec.api import MtecApiError
from custom_components.mtec.climate import MtecClimate, PRESET_DAY, PRESET_NIGHT
from custom_components.mtec.const import HeatCircuitMode


def test_climate_hvac_mode_day(coordinator_data):
    """Test HVAC mode when M-TEC mode is Day."""
    coordinator = MagicMock()
    coordinator_data["hc0_mode"] = HeatCircuitMode.DAY
    coordinator.data = coordinator_data
    coordinator.last_update_success = True
    coordinator.client.host = "192.168.1.100"
    
    circuit = {
        "circuit": 0,
        "mode_key": "hc0_mode",
        "room_temp_key": "hc0_room_temp",
        "room_set_temp_key": "hc0_room_set_temp",
        "day_temp_key": "hc0_day_temp",
        "night_temp_key": "hc0_night_temp",
        "translation_key": "hc0_climate",
    }
    
    climate = MtecClimate(coordinator, circuit)
    assert climate.hvac_mode == HVACMode.HEAT


def test_climate_hvac_mode_standby(coordinator_data):
    """Test HVAC mode when M-TEC mode is Standby."""
    coordinator = MagicMock()
    coordinator_data["hc0_mode"] = HeatCircuitMode.STANDBY
    coordinator.data = coordinator_data
    coordinator.last_update_success = True
    coordinator.client.host = "192.168.1.100"
    
    circuit = {
        "circuit": 0,
        "mode_key": "hc0_mode",
        "room_temp_key": "hc0_room_temp",
        "room_set_temp_key": "hc0_room_set_temp",
        "day_temp_key": "hc0_day_temp",
        "night_temp_key": "hc0_night_temp",
        "translation_key": "hc0_climate",
    }
    
    climate = MtecClimate(coordinator, circuit)
    assert climate.hvac_mode == HVACMode.OFF


def test_climate_hvac_mode_timer(coordinator_data):
    """Test HVAC mode when M-TEC mode is Timer."""
    coordinator = MagicMock()
    coordinator_data["hc0_mode"] = HeatCircuitMode.TIMER
    coordinator.data = coordinator_data
    coordinator.last_update_success = True
    coordinator.client.host = "192.168.1.100"
    
    circuit = {
        "circuit": 0,
        "mode_key": "hc0_mode",
        "room_temp_key": "hc0_room_temp",
        "room_set_temp_key": "hc0_room_set_temp",
        "day_temp_key": "hc0_day_temp",
        "night_temp_key": "hc0_night_temp",
        "translation_key": "hc0_climate",
    }
    
    climate = MtecClimate(coordinator, circuit)
    assert climate.hvac_mode == HVACMode.AUTO


def test_climate_current_temperature(coordinator_data):
    """Test current temperature."""
    coordinator = MagicMock()
    coordinator.data = coordinator_data
    coordinator.last_update_success = True
    coordinator.client.host = "192.168.1.100"
    
    circuit = {
        "circuit": 0,
        "mode_key": "hc0_mode",
        "room_temp_key": "hc0_room_temp",
        "room_set_temp_key": "hc0_room_set_temp",
        "day_temp_key": "hc0_day_temp",
        "night_temp_key": "hc0_night_temp",
        "translation_key": "hc0_climate",
    }
    
    climate = MtecClimate(coordinator, circuit)
    assert climate.current_temperature == 22.0


def test_climate_target_temperature(coordinator_data):
    """Test target temperature."""
    coordinator = MagicMock()
    coordinator.data = coordinator_data
    coordinator.last_update_success = True
    coordinator.client.host = "192.168.1.100"
    
    circuit = {
        "circuit": 0,
        "mode_key": "hc0_mode",
        "room_temp_key": "hc0_room_temp",
        "room_set_temp_key": "hc0_room_set_temp",
        "day_temp_key": "hc0_day_temp",
        "night_temp_key": "hc0_night_temp",
        "translation_key": "hc0_climate",
    }
    
    climate = MtecClimate(coordinator, circuit)
    assert climate.target_temperature == 21.0


def test_climate_preset_mode(coordinator_data):
    """Test preset mode mapping."""
    coordinator = MagicMock()
    coordinator_data["hc0_mode"] = HeatCircuitMode.DAY
    coordinator.data = coordinator_data
    coordinator.last_update_success = True
    coordinator.client.host = "192.168.1.100"
    
    circuit = {
        "circuit": 0,
        "mode_key": "hc0_mode",
        "room_temp_key": "hc0_room_temp",
        "room_set_temp_key": "hc0_room_set_temp",
        "day_temp_key": "hc0_day_temp",
        "night_temp_key": "hc0_night_temp",
        "translation_key": "hc0_climate",
    }
    
    climate = MtecClimate(coordinator, circuit)
    assert climate.preset_mode == PRESET_DAY


def test_climate_preset_mode_night(coordinator_data):
    """Test preset mode for Night."""
    coordinator = MagicMock()
    coordinator_data["hc0_mode"] = HeatCircuitMode.NIGHT
    coordinator.data = coordinator_data
    coordinator.last_update_success = True
    coordinator.client.host = "192.168.1.100"
    
    circuit = {
        "circuit": 0,
        "mode_key": "hc0_mode",
        "room_temp_key": "hc0_room_temp",
        "room_set_temp_key": "hc0_room_set_temp",
        "day_temp_key": "hc0_day_temp",
        "night_temp_key": "hc0_night_temp",
        "translation_key": "hc0_climate",
    }
    
    climate = MtecClimate(coordinator, circuit)
    assert climate.preset_mode == PRESET_NIGHT


def test_climate_unique_id(coordinator_data):
    """Test unique ID."""
    coordinator = MagicMock()
    coordinator.data = coordinator_data
    coordinator.last_update_success = True
    coordinator.client.host = "192.168.1.100"
    
    circuit = {
        "circuit": 0,
        "mode_key": "hc0_mode",
        "room_temp_key": "hc0_room_temp",
        "room_set_temp_key": "hc0_room_set_temp",
        "day_temp_key": "hc0_day_temp",
        "night_temp_key": "hc0_night_temp",
        "translation_key": "hc0_climate",
    }
    
    climate = MtecClimate(coordinator, circuit)
    assert climate.unique_id == "192.168.1.100_hc0_climate"


async def test_climate_set_hvac_mode(coordinator_data):
    """Test setting HVAC mode."""
    coordinator = MagicMock()
    coordinator.data = coordinator_data
    coordinator.last_update_success = True
    coordinator.client.host = "192.168.1.100"
    coordinator.async_request_refresh = AsyncMock()
    coordinator.client.async_write_value = AsyncMock()
    
    circuit = {
        "circuit": 0,
        "mode_key": "hc0_mode",
        "room_temp_key": "hc0_room_temp",
        "room_set_temp_key": "hc0_room_set_temp",
        "day_temp_key": "hc0_day_temp",
        "night_temp_key": "hc0_night_temp",
        "translation_key": "hc0_climate",
    }
    
    climate = MtecClimate(coordinator, circuit)
    await climate.async_set_hvac_mode(HVACMode.OFF)
    
    # OFF should map to STANDBY (0)
    coordinator.client.async_write_value.assert_called_once_with("hc0_mode", 0.0)
    coordinator.async_request_refresh.assert_called_once()


async def test_climate_set_temperature(coordinator_data):
    """Test setting temperature."""
    coordinator = MagicMock()
    coordinator.data = coordinator_data
    coordinator.last_update_success = True
    coordinator.client.host = "192.168.1.100"
    coordinator.async_request_refresh = AsyncMock()
    coordinator.client.async_write_value = AsyncMock()
    
    circuit = {
        "circuit": 0,
        "mode_key": "hc0_mode",
        "room_temp_key": "hc0_room_temp",
        "room_set_temp_key": "hc0_room_set_temp",
        "day_temp_key": "hc0_day_temp",
        "night_temp_key": "hc0_night_temp",
        "translation_key": "hc0_climate",
    }
    
    climate = MtecClimate(coordinator, circuit)
    await climate.async_set_temperature(temperature=23.0)
    
    # Should write to day temp since current mode is Day
    coordinator.client.async_write_value.assert_called_once_with("hc0_day_temp", 23.0)
    coordinator.async_request_refresh.assert_called_once()


async def test_climate_set_temperature_night_mode(coordinator_data):
    """Test setting temperature in night mode."""
    coordinator = MagicMock()
    coordinator_data["hc0_mode"] = HeatCircuitMode.NIGHT
    coordinator.data = coordinator_data
    coordinator.last_update_success = True
    coordinator.client.host = "192.168.1.100"
    coordinator.async_request_refresh = AsyncMock()
    coordinator.client.async_write_value = AsyncMock()
    
    circuit = {
        "circuit": 0,
        "mode_key": "hc0_mode",
        "room_temp_key": "hc0_room_temp",
        "room_set_temp_key": "hc0_room_set_temp",
        "day_temp_key": "hc0_day_temp",
        "night_temp_key": "hc0_night_temp",
        "translation_key": "hc0_climate",
    }
    
    climate = MtecClimate(coordinator, circuit)
    await climate.async_set_temperature(temperature=18.5)
    
    # Should write to night temp since current mode is Night
    coordinator.client.async_write_value.assert_called_once_with("hc0_night_temp", 18.5)


async def test_climate_set_preset_mode(coordinator_data):
    """Test setting preset mode."""
    coordinator = MagicMock()
    coordinator.data = coordinator_data
    coordinator.last_update_success = True
    coordinator.client.host = "192.168.1.100"
    coordinator.async_request_refresh = AsyncMock()
    coordinator.client.async_write_value = AsyncMock()
    
    circuit = {
        "circuit": 0,
        "mode_key": "hc0_mode",
        "room_temp_key": "hc0_room_temp",
        "room_set_temp_key": "hc0_room_set_temp",
        "day_temp_key": "hc0_day_temp",
        "night_temp_key": "hc0_night_temp",
        "translation_key": "hc0_climate",
    }
    
    climate = MtecClimate(coordinator, circuit)
    await climate.async_set_preset_mode(PRESET_NIGHT)
    
    # NIGHT preset should map to mode 3
    coordinator.client.async_write_value.assert_called_once_with("hc0_mode", 3.0)
    coordinator.async_request_refresh.assert_called_once()


async def test_climate_set_hvac_mode_error(coordinator_data, caplog):
    """Test setting HVAC mode with API error."""
    coordinator = MagicMock()
    coordinator.data = coordinator_data
    coordinator.last_update_success = True
    coordinator.client.host = "192.168.1.100"
    coordinator.async_request_refresh = AsyncMock()
    coordinator.client.async_write_value = AsyncMock(
        side_effect=MtecApiError("Write failed")
    )
    
    circuit = {
        "circuit": 0,
        "mode_key": "hc0_mode",
        "room_temp_key": "hc0_room_temp",
        "room_set_temp_key": "hc0_room_set_temp",
        "day_temp_key": "hc0_day_temp",
        "night_temp_key": "hc0_night_temp",
        "translation_key": "hc0_climate",
    }
    
    climate = MtecClimate(coordinator, circuit)
    await climate.async_set_hvac_mode(HVACMode.OFF)
    
    assert "Failed to set HC0 mode" in caplog.text
    coordinator.async_request_refresh.assert_not_called()


def test_climate_hvac_modes():
    """Test available HVAC modes."""
    coordinator = MagicMock()
    coordinator.data = {}
    coordinator.last_update_success = True
    coordinator.client.host = "192.168.1.100"
    
    circuit = {
        "circuit": 0,
        "mode_key": "hc0_mode",
        "room_temp_key": "hc0_room_temp",
        "room_set_temp_key": "hc0_room_set_temp",
        "day_temp_key": "hc0_day_temp",
        "night_temp_key": "hc0_night_temp",
        "translation_key": "hc0_climate",
    }
    
    climate = MtecClimate(coordinator, circuit)
    assert HVACMode.OFF in climate.hvac_modes
    assert HVACMode.AUTO in climate.hvac_modes
    assert HVACMode.HEAT in climate.hvac_modes


def test_climate_preset_modes():
    """Test available preset modes."""
    coordinator = MagicMock()
    coordinator.data = {}
    coordinator.last_update_success = True
    coordinator.client.host = "192.168.1.100"
    
    circuit = {
        "circuit": 0,
        "mode_key": "hc0_mode",
        "room_temp_key": "hc0_room_temp",
        "room_set_temp_key": "hc0_room_set_temp",
        "day_temp_key": "hc0_day_temp",
        "night_temp_key": "hc0_night_temp",
        "translation_key": "hc0_climate",
    }
    
    climate = MtecClimate(coordinator, circuit)
    assert PRESET_DAY in climate.preset_modes
    assert PRESET_NIGHT in climate.preset_modes
