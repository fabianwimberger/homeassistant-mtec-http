"""Test fixtures for M-TEC Heat Pump integration."""

from __future__ import annotations

import pytest
import respx
from homeassistant.core import HomeAssistant
from httpx import Response


def pytest_configure(config):
    """Configure pytest."""
    config.addinivalue_line("markers", "asyncio: mark test as async")


@pytest.fixture(autouse=True)
def auto_enable_custom_integrations(enable_custom_integrations):
    """Enable custom integrations in Home Assistant."""
    yield


@pytest.fixture
async def hass(hass: HomeAssistant) -> HomeAssistant:
    """Return a Home Assistant instance."""
    return hass


@pytest.fixture
def mock_api_respx():
    """Create a mock M-TEC API using respx."""
    with respx.mock(assert_all_mocked=False) as rsps:
        # Default handler for read requests
        def read_handler(request):
            import json

            body = json.loads(request.content)
            response = []
            for item in body:
                name = item.get("name", "")
                if "outdoorTemp" in name:
                    response.append({"name": name, "value": "15.5"})
                elif "applVersion" in name:
                    response.append({"name": name, "value": "1.33.7.0"})
                elif "systemSerialNumber" in name:
                    response.append({"name": name, "value": "WP123456"})
                elif "heatpumpState" in name:
                    response.append({"name": name, "value": "2"})
                elif "power" in name and "Heat" in name:
                    response.append({"name": name, "value": "3500"})
                elif "power" in name and "Electric" in name:
                    response.append({"name": name, "value": "850"})
                elif "Temp" in name or "temp" in name:
                    response.append({"name": name, "value": "22.5"})
                elif "pump" in name.lower() or "Pump" in name:
                    response.append({"name": name, "value": "1"})
                elif "mode" in name.lower() or "Mode" in name:
                    response.append({"name": name, "value": "2"})
                else:
                    response.append({"name": name, "value": "0"})
            return Response(200, json=response)

        # Default handler for write requests
        def write_handler(request):
            return Response(200, json=[{"success": True}])

        # Register routes
        rsps.route(method="POST", url__startswith="http://").mock(side_effect=read_handler)

        yield rsps


@pytest.fixture
def mock_api_respx_with_missing_signals():
    """Create a mock API that simulates missing signals."""
    available_signals = {
        "APPL.CtrlAppl.sParam.outdoorTemp.values.actValue",
        "APPL.CtrlAppl.sParam.heatpump[0].values.heatpumpState",
        "APPL.CtrlAppl.sParam.param.applVersion",
        "APPL.CtrlAppl.sParam.param.systemSerialNumber",
    }

    with respx.mock(assert_all_mocked=False) as rsps:

        def handler(request):
            import json

            body = json.loads(request.content)
            # Check if any requested signal is unavailable
            for item in body:
                if item.get("name") not in available_signals:
                    return Response(500)

            response = []
            for item in body:
                name = item.get("name", "")
                if "outdoorTemp" in name:
                    response.append({"name": name, "value": "15.5"})
                elif "applVersion" in name:
                    response.append({"name": name, "value": "1.33.7.0"})
                elif "systemSerialNumber" in name:
                    response.append({"name": name, "value": "WP123456"})
                elif "heatpumpState" in name:
                    response.append({"name": name, "value": "2"})
                else:
                    response.append({"name": name, "value": "0"})
            return Response(200, json=response)

        rsps.route(method="POST", url__startswith="http://").mock(side_effect=handler)
        yield rsps


@pytest.fixture
def coordinator_data():
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
