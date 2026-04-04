"""Test fixtures for M-TEC Heat Pump integration."""
from __future__ import annotations

import pytest
from aiohttp import web
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from custom_components.mtec.api import MtecApiClient
from custom_components.mtec.const import DOMAIN


def pytest_configure(config):
    """Configure pytest."""
    config.addinivalue_line(
        "markers", "asyncio: mark test as async"
    )


@pytest.fixture
async def hass(hass: HomeAssistant) -> HomeAssistant:
    """Return a Home Assistant instance."""
    return hass


@pytest.fixture
async def mock_api_server(aiohttp_server):
    """Create a mock M-TEC API server."""
    async def handler(request):
        """Handle API requests."""
        if request.path == "/var/readWriteVars":
            if request.query.get("action") == "set":
                # Write operation
                return web.json_response([{"success": True}])
            
            # Read operation
            body = await request.json()
            response = []
            for item in body:
                name = item.get("name", "")
                # Return realistic values based on signal name
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
            return web.json_response(response)
        return web.Response(status=404)

    app = web.Application()
    app.router.add_post("/var/readWriteVars", handler)
    server = await aiohttp_server(app)
    return server


@pytest.fixture
async def mock_api_server_with_missing_signals(aiohttp_server):
    """Create a mock API server that simulates missing signals."""
    available_signals = {
        "APPL.CtrlAppl.sParam.outdoorTemp.values.actValue",
        "APPL.CtrlAppl.sParam.heatpump[0].values.heatpumpState",
        "APPL.CtrlAppl.sParam.param.applVersion",
        "APPL.CtrlAppl.sParam.param.systemSerialNumber",
    }
    
    async def handler(request):
        """Handle API requests."""
        if request.path == "/var/readWriteVars":
            body = await request.json()
            # Check if any requested signal is unavailable
            for item in body:
                if item.get("name") not in available_signals:
                    return web.Response(status=500)
            
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
            return web.json_response(response)
        return web.Response(status=404)

    app = web.Application()
    app.router.add_post("/var/readWriteVars", handler)
    server = await aiohttp_server(app)
    return server


@pytest.fixture
async def api_client(mock_api_server, hass: HomeAssistant):
    """Create an API client connected to mock server."""
    session = async_get_clientsession(hass)
    client = MtecApiClient(f"localhost:{mock_api_server.port}", session)
    return client


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
