"""Test fixtures for M-TEC Heat Pump integration."""

from __future__ import annotations

from collections.abc import Generator

import pytest
from homeassistant.core import HomeAssistant


def pytest_configure(config: pytest.Config) -> None:
    """Configure pytest."""
    config.addinivalue_line("markers", "asyncio: mark test as async")


@pytest.fixture(autouse=True)
def auto_enable_custom_integrations(enable_custom_integrations: None) -> Generator[None]:
    """Enable custom integrations in Home Assistant."""
    yield


@pytest.fixture
async def hass(hass: HomeAssistant) -> HomeAssistant:
    """Return a Home Assistant instance."""
    return hass


@pytest.fixture
def coordinator_data() -> dict[str, float | int]:
    """Return sample coordinator data."""
    return {
        "outdoor_temp": 15.5,
        "heating_power": 3.5,
        "electrical_power": 850,
        "heatpump_state": 2,
        "temp_heat_flow": 35.0,
        "temp_heat_return": 30.0,
        "hc0_mode": 2,
        "hc0_room_temp": 22.0,
        "hc0_room_set_temp": 21.0,
        "hc0_day_temp": 21.0,
        "hc0_night_temp": 18.0,
        "hc1_mode": 1,
        "hc1_room_temp": 21.5,
        "hc1_room_set_temp": 20.5,
        "system_operating_mode": 2,
        "hot_water_mode": 1,
        "hot_water_top_temp": 45.0,
        "hot_water_target_temp": 48.0,
        "buffer_heat_request": 1,
        "hot_water_heat_request": 0,
        "hc0_pump": 1,
        "hc1_pump": 0,
    }
