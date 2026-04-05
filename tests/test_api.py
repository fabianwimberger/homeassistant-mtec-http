"""Tests for M-TEC API client."""

from __future__ import annotations

from typing import Any

import pytest
from aioresponses import CallbackResult, aioresponses
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from custom_components.mtec.api import MtecApiClient, MtecApiError
from custom_components.mtec.const import SIGNAL_MAP


async def test_api_client_init() -> None:
    """Test API client initialization."""
    client = MtecApiClient("192.168.1.100", None)
    assert client.host == "192.168.1.100"
    assert client._base_url == "http://192.168.1.100/var/readWriteVars"


async def test_api_client_init_with_port() -> None:
    """Test API client initialization with port."""
    client = MtecApiClient("192.168.1.100:8080", None)
    assert client.host == "192.168.1.100:8080"
    assert client._base_url == "http://192.168.1.100:8080/var/readWriteVars"


async def test_validate_connection_success(hass: HomeAssistant) -> None:
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


async def test_validate_connection_failure(hass: HomeAssistant) -> None:
    """Test connection validation with server error."""
    with aioresponses() as m:
        m.post("http://192.168.1.100/var/readWriteVars", status=500)
        session = async_get_clientsession(hass)
        client = MtecApiClient("192.168.1.100", session)

        result = await client.async_validate_connection()
        assert result is False


async def test_read_device_info(hass: HomeAssistant) -> None:
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


async def test_probe_available_keys(hass: HomeAssistant) -> None:
    """Test probing available signal keys."""
    with aioresponses() as m:
        m.post("http://192.168.1.100/var/readWriteVars", payload=[{"name": "test", "value": "1"}])

        session = async_get_clientsession(hass)
        client = MtecApiClient("192.168.1.100", session)

        available = await client.async_probe_available_keys()
        # The test will return success for all signals since we mock all responses as 200
        assert len(available) > 0


async def test_read_values(hass: HomeAssistant) -> None:
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


async def test_write_value(hass: HomeAssistant) -> None:
    """Test writing a value to the API."""
    with aioresponses() as m:
        m.post("http://192.168.1.100/var/readWriteVars?action=set", payload=[{"success": True}])
        session = async_get_clientsession(hass)
        client = MtecApiClient("192.168.1.100", session)

        # Should not raise
        await client.async_write_value("hc0_day_temp", 22.0)


async def test_write_value_unknown_key(hass: HomeAssistant) -> None:
    """Test writing to an unknown signal key."""
    session = async_get_clientsession(hass)
    client = MtecApiClient("192.168.1.100", session)

    with pytest.raises(MtecApiError, match="Unknown signal key"):
        await client.async_write_value("unknown_key", 22.0)


async def test_read_values_http_error(hass: HomeAssistant) -> None:
    """Test handling HTTP errors."""
    with aioresponses() as m:
        m.post("http://192.168.1.100/var/readWriteVars", status=500)
        session = async_get_clientsession(hass)
        client = MtecApiClient("192.168.1.100", session)
        client._available_keys = {"outdoor_temp"}  # Set available keys directly

        with pytest.raises(MtecApiError, match="HTTP 500"):
            await client.async_read_values(["outdoor_temp"])


async def test_parse_value_bool() -> None:
    """Test parsing boolean values."""
    from custom_components.mtec.api import _parse_value

    assert _parse_value(True) == 1.0
    assert _parse_value(False) == 0.0


async def test_parse_value_string_bool() -> None:
    """Test parsing string boolean values."""
    from custom_components.mtec.api import _parse_value

    assert _parse_value("true") == 1.0
    assert _parse_value("false") == 0.0


async def test_parse_value_numeric() -> None:
    """Test parsing numeric values."""
    from custom_components.mtec.api import _parse_value

    assert _parse_value(42) == 42.0
    assert _parse_value(3.14) == 3.14
    assert _parse_value("123.45") == 123.45


async def test_parse_value_invalid() -> None:
    """Test parsing invalid values."""
    from custom_components.mtec.api import _parse_value

    assert _parse_value("not a number") is None
    assert _parse_value(None) is None
    assert _parse_value([1, 2, 3]) is None


async def test_available_keys_property(hass: HomeAssistant) -> None:
    """Test available_keys property returns empty set before probing."""
    session = async_get_clientsession(hass)
    client = MtecApiClient("192.168.1.100", session)

    assert client.available_keys == set()

    client._available_keys = {"outdoor_temp", "hc0_mode"}
    assert client.available_keys == {"outdoor_temp", "hc0_mode"}


async def test_write_value_http_error(hass: HomeAssistant) -> None:
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


async def test_probe_partial_availability(hass: HomeAssistant) -> None:
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


async def test_read_device_info_with_failure(hass: HomeAssistant) -> None:
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


async def test_probe_phantom_heat_circuits_filtered(hass: HomeAssistant) -> None:
    """Test that phantom heat circuits (flow_set_temp == 0) are filtered out."""

    # Helper to generate heat circuit signals
    def get_hc_signals(hc_num: int) -> list[str]:
        """Get all signal keys for a heat circuit."""
        return [k for k in SIGNAL_MAP if k.startswith(f"hc{hc_num}_")]

    with aioresponses() as m:
        # Track which signals get probed
        probed_values: dict[str, float] = {}

        def callback(url: str, **kwargs: Any) -> CallbackResult:
            """Return different values based on the signal being requested."""
            import json

            # Get request body from json parameter
            request_data = kwargs.get("json")
            if request_data is None:
                # Try to get from raw data
                data = kwargs.get("data")
                if data:
                    request_data = json.loads(data)
            signal_name = request_data[0]["name"] if request_data else ""
            key = None
            for k, v in SIGNAL_MAP.items():
                if v == signal_name:
                    key = k
                    break

            # Default value for most signals
            value = 1.0

            # HC0: real circuit with non-zero flow_set_temp
            if key == "hc0_flow_set_temp":
                value = 29.2
            elif key and key.startswith("hc0_"):
                value = 21.5 if "temp" in key else 1.0

            # HC1: real circuit with non-zero flow_set_temp
            elif key == "hc1_flow_set_temp":
                value = 27.0
            elif key and key.startswith("hc1_"):
                value = 20.0 if "temp" in key else 1.0

            # HC2: phantom circuit with zero flow_set_temp
            elif key == "hc2_flow_set_temp" or (key and key.startswith("hc2_")):
                value = 0.0

            if key:
                probed_values[key] = value

            return CallbackResult(payload=[{"name": signal_name, "value": str(value)}])

        # Mock all requests to the API endpoint
        m.post("http://192.168.1.100/var/readWriteVars", callback=callback, repeat=True)

        session = async_get_clientsession(hass)
        client = MtecApiClient("192.168.1.100", session)

        available = await client.async_probe_available_keys()

        # Verify hc2_flow_set_temp was probed with value 0
        assert "hc2_flow_set_temp" in probed_values
        assert probed_values["hc2_flow_set_temp"] == 0.0

        # Verify hc0_flow_set_temp and hc1_flow_set_temp were probed with non-zero
        assert probed_values.get("hc0_flow_set_temp") == 29.2
        assert probed_values.get("hc1_flow_set_temp") == 27.0

        # HC0 and HC1 should be available (non-zero flow_set_temp)
        hc0_signals = get_hc_signals(0)
        hc1_signals = get_hc_signals(1)
        for sig in hc0_signals:
            assert sig in available, f"Expected {sig} to be available"
        for sig in hc1_signals:
            assert sig in available, f"Expected {sig} to be available"

        # HC2 should be filtered out (flow_set_temp == 0)
        hc2_signals = get_hc_signals(2)
        for sig in hc2_signals:
            assert sig not in available, f"Expected {sig} to be filtered out"
