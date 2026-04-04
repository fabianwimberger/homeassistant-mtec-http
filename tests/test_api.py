"""Tests for M-TEC API client."""
from __future__ import annotations

import pytest
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from custom_components.mtec.api import MtecApiClient, MtecApiError


async def test_api_client_init():
    """Test API client initialization."""
    client = MtecApiClient("192.168.1.100", None)
    assert client.host == "192.168.1.100"
    assert client._base_url == "http://192.168.1.100/var/readWriteVars"


async def test_api_client_init_with_port():
    """Test API client initialization with port."""
    client = MtecApiClient("192.168.1.100:8080", None)
    assert client.host == "192.168.1.100:8080"
    assert client._base_url == "http://192.168.1.100:8080/var/readWriteVars"


async def test_validate_connection_success(mock_api_server, hass: HomeAssistant):
    """Test successful connection validation."""
    session = async_get_clientsession(hass)
    client = MtecApiClient(f"localhost:{mock_api_server.port}", session)
    
    result = await client.async_validate_connection()
    assert result is True


async def test_validate_connection_failure(aiohttp_server, hass: HomeAssistant):
    """Test connection validation with server error."""
    from aiohttp import web
    
    async def handler(request):
        return web.Response(status=500)
    
    app = web.Application()
    app.router.add_post("/var/readWriteVars", handler)
    server = await aiohttp_server(app)
    
    session = async_get_clientsession(hass)
    client = MtecApiClient(f"localhost:{server.port}", session)
    
    result = await client.async_validate_connection()
    assert result is False


async def test_validate_connection_timeout(aiohttp_server, hass: HomeAssistant):
    """Test connection validation timeout."""
    import asyncio
    from aiohttp import web
    
    async def slow_handler(request):
        await asyncio.sleep(20)
        return web.json_response([])
    
    app = web.Application()
    app.router.add_post("/var/readWriteVars", slow_handler)
    server = await aiohttp_server(app)
    
    session = async_get_clientsession(hass)
    client = MtecApiClient(f"localhost:{server.port}", session)
    
    result = await client.async_validate_connection()
    assert result is False


async def test_read_device_info(mock_api_server, hass: HomeAssistant):
    """Test reading device info."""
    session = async_get_clientsession(hass)
    client = MtecApiClient(f"localhost:{mock_api_server.port}", session)
    
    signals = {
        "firmware_version": "APPL.CtrlAppl.sParam.param.applVersion",
        "serial_number": "APPL.CtrlAppl.sParam.param.systemSerialNumber",
    }
    
    result = await client.async_read_device_info(signals)
    assert result["firmware_version"] == "1.33.7.0"
    assert result["serial_number"] == "WP123456"


async def test_probe_available_keys(mock_api_server, hass: HomeAssistant):
    """Test probing available signal keys."""
    session = async_get_clientsession(hass)
    client = MtecApiClient(f"localhost:{mock_api_server.port}", session)
    
    available = await client.async_probe_available_keys()
    assert len(available) > 0
    assert "outdoor_temp" in available
    assert "heatpump_state" in available


async def test_probe_available_keys_with_missing(
    mock_api_server_with_missing_signals, hass: HomeAssistant
):
    """Test probing with some unavailable signals."""
    session = async_get_clientsession(hass)
    client = MtecApiClient(
        f"localhost:{mock_api_server_with_missing_signals.port}", session
    )
    
    available = await client.async_probe_available_keys()
    # Should only contain signals that don't return 500
    assert "outdoor_temp" in available
    assert "heatpump_state" in available


async def test_read_values(mock_api_server, hass: HomeAssistant):
    """Test reading values from the API."""
    session = async_get_clientsession(hass)
    client = MtecApiClient(f"localhost:{mock_api_server.port}", session)
    
    # First probe available keys
    await client.async_probe_available_keys()
    
    # Then read values
    values = await client.async_read_values()
    assert "outdoor_temp" in values
    assert values["outdoor_temp"] == 15.5


async def test_read_values_specific_keys(mock_api_server, hass: HomeAssistant):
    """Test reading specific keys."""
    session = async_get_clientsession(hass)
    client = MtecApiClient(f"localhost:{mock_api_server.port}", session)
    
    await client.async_probe_available_keys()
    values = await client.async_read_values(["outdoor_temp", "heating_power"])
    
    assert "outdoor_temp" in values
    assert values["outdoor_temp"] == 15.5


async def test_write_value(mock_api_server, hass: HomeAssistant):
    """Test writing a value to the API."""
    session = async_get_clientsession(hass)
    client = MtecApiClient(f"localhost:{mock_api_server.port}", session)
    
    # Should not raise
    await client.async_write_value("hc0_day_temp", 22.0)


async def test_write_value_unknown_key(mock_api_server, hass: HomeAssistant):
    """Test writing to an unknown signal key."""
    session = async_get_clientsession(hass)
    client = MtecApiClient(f"localhost:{mock_api_server.port}", session)
    
    with pytest.raises(MtecApiError, match="Unknown signal key"):
        await client.async_write_value("unknown_key", 22.0)


async def test_read_values_http_error(aiohttp_server, hass: HomeAssistant):
    """Test handling HTTP errors."""
    from aiohttp import web
    
    async def handler(request):
        return web.Response(status=500)
    
    app = web.Application()
    app.router.add_post("/var/readWriteVars", handler)
    server = await aiohttp_server(app)
    
    session = async_get_clientsession(hass)
    client = MtecApiClient(f"localhost:{server.port}", session)
    
    with pytest.raises(MtecApiError, match="HTTP 500"):
        await client.async_read_values(["outdoor_temp"])


async def test_parse_value_bool():
    """Test parsing boolean values."""
    from custom_components.mtec.api import _parse_value
    
    assert _parse_value(True) == 1.0
    assert _parse_value(False) == 0.0


async def test_parse_value_string_bool():
    """Test parsing string boolean values."""
    from custom_components.mtec.api import _parse_value
    
    assert _parse_value("true") == 1.0
    assert _parse_value("false") == 0.0


async def test_parse_value_numeric():
    """Test parsing numeric values."""
    from custom_components.mtec.api import _parse_value
    
    assert _parse_value(42) == 42.0
    assert _parse_value(3.14) == 3.14
    assert _parse_value("123.45") == 123.45


async def test_parse_value_invalid():
    """Test parsing invalid values."""
    from custom_components.mtec.api import _parse_value
    
    assert _parse_value("not a number") is None
    assert _parse_value(None) is None
    assert _parse_value([1, 2, 3]) is None
