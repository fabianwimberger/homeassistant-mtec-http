"""Tests for M-TEC API client."""

from __future__ import annotations

import pytest
from aioresponses import aioresponses
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


async def test_validate_connection_success(hass: HomeAssistant):
    """Test successful connection validation."""
    with aioresponses() as m:
        m.post(
            "http://192.168.1.100/var/readWriteVars",
            payload=[{"name": "APPL.CtrlAppl.sParam.outdoorTemp.values.actValue", "value": "15.5"}],
        )
        session = async_get_clientsession(hass)
        client = MtecApiClient("192.168.1.100", session)

        result = await client.async_validate_connection()
        assert result is True


async def test_validate_connection_failure(hass: HomeAssistant):
    """Test connection validation with server error."""
    with aioresponses() as m:
        m.post("http://192.168.1.100/var/readWriteVars", status=500)
        session = async_get_clientsession(hass)
        client = MtecApiClient("192.168.1.100", session)

        result = await client.async_validate_connection()
        assert result is False


async def test_read_device_info(hass: HomeAssistant):
    """Test reading device info."""
    with aioresponses() as m:
        m.post(
            "http://192.168.1.100/var/readWriteVars",
            payload=[{"name": "APPL.CtrlAppl.sParam.param.applVersion", "value": "1.33.7.0"}],
        )
        session = async_get_clientsession(hass)
        client = MtecApiClient("192.168.1.100", session)

        signals = {
            "firmware_version": "APPL.CtrlAppl.sParam.param.applVersion",
        }

        result = await client.async_read_device_info(signals)
        assert result["firmware_version"] == "1.33.7.0"


async def test_probe_available_keys(hass: HomeAssistant):
    """Test probing available signal keys."""
    with aioresponses() as m:
        m.post("http://192.168.1.100/var/readWriteVars", payload=[{"name": "test", "value": "1"}])

        session = async_get_clientsession(hass)
        client = MtecApiClient("192.168.1.100", session)

        available = await client.async_probe_available_keys()
        # The test will return success for all signals since we mock all responses as 200
        assert len(available) > 0


async def test_read_values(hass: HomeAssistant):
    """Test reading values from the API."""
    with aioresponses() as m:
        m.post(
            "http://192.168.1.100/var/readWriteVars",
            payload=[{"name": "APPL.CtrlAppl.sParam.outdoorTemp.values.actValue", "value": "15.5"}],
        )
        session = async_get_clientsession(hass)
        client = MtecApiClient("192.168.1.100", session)
        client._available_keys = {"outdoor_temp"}  # Set available keys directly

        values = await client.async_read_values(["outdoor_temp"])
        assert "outdoor_temp" in values
        assert values["outdoor_temp"] == 15.5


async def test_write_value(hass: HomeAssistant):
    """Test writing a value to the API."""
    with aioresponses() as m:
        m.post("http://192.168.1.100/var/readWriteVars?action=set", payload=[{"success": True}])
        session = async_get_clientsession(hass)
        client = MtecApiClient("192.168.1.100", session)

        # Should not raise
        await client.async_write_value("hc0_day_temp", 22.0)


async def test_write_value_unknown_key(hass: HomeAssistant):
    """Test writing to an unknown signal key."""
    session = async_get_clientsession(hass)
    client = MtecApiClient("192.168.1.100", session)

    with pytest.raises(MtecApiError, match="Unknown signal key"):
        await client.async_write_value("unknown_key", 22.0)


async def test_read_values_http_error(hass: HomeAssistant):
    """Test handling HTTP errors."""
    with aioresponses() as m:
        m.post("http://192.168.1.100/var/readWriteVars", status=500)
        session = async_get_clientsession(hass)
        client = MtecApiClient("192.168.1.100", session)
        client._available_keys = {"outdoor_temp"}  # Set available keys directly

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


async def test_available_keys_property(hass: HomeAssistant):
    """Test available_keys property returns empty set before probing."""
    session = async_get_clientsession(hass)
    client = MtecApiClient("192.168.1.100", session)

    assert client.available_keys == set()

    client._available_keys = {"outdoor_temp", "hc0_mode"}
    assert client.available_keys == {"outdoor_temp", "hc0_mode"}


async def test_write_value_http_error(hass: HomeAssistant):
    """Test writing a value when server returns error."""
    with aioresponses() as m:
        m.post(
            "http://192.168.1.100/var/readWriteVars?action=set",
            status=500,
        )
        session = async_get_clientsession(hass)
        client = MtecApiClient("192.168.1.100", session)

        with pytest.raises(MtecApiError, match="HTTP 500"):
            await client.async_write_value("hc0_day_temp", 22.0)


async def test_probe_partial_availability(hass: HomeAssistant):
    """Test probing where some signals return 500 (unavailable)."""
    with aioresponses() as m:
        # Mock first call as success, rest as 500
        m.post(
            "http://192.168.1.100/var/readWriteVars",
            payload=[{"name": "test", "value": "15.5"}],
        )
        # All subsequent calls return 500
        for _ in range(200):
            m.post("http://192.168.1.100/var/readWriteVars", status=500)

        session = async_get_clientsession(hass)
        client = MtecApiClient("192.168.1.100", session)

        available = await client.async_probe_available_keys()
        # Only the first signal should succeed
        assert len(available) == 1


async def test_read_device_info_with_failure(hass: HomeAssistant):
    """Test reading device info when some signals fail."""
    with aioresponses() as m:
        m.post(
            "http://192.168.1.100/var/readWriteVars",
            payload=[{"name": "APPL.CtrlAppl.sParam.param.applVersion", "value": "1.0.0"}],
        )
        m.post("http://192.168.1.100/var/readWriteVars", status=500)

        session = async_get_clientsession(hass)
        client = MtecApiClient("192.168.1.100", session)

        signals = {
            "firmware_version": "APPL.CtrlAppl.sParam.param.applVersion",
            "serial_number": "APPL.CtrlAppl.sParam.param.systemSerialNumber",
        }
        result = await client.async_read_device_info(signals)

        assert result["firmware_version"] == "1.0.0"
        assert "serial_number" not in result
