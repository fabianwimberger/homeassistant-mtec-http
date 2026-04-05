"""Tests for M-TEC config flow."""

from __future__ import annotations

from unittest.mock import patch

import voluptuous as vol
from homeassistant.config_entries import SOURCE_RECONFIGURE, SOURCE_USER
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResultType

from custom_components.mtec.const import (
    CONF_HOST,
    CONF_SCAN_INTERVAL,
    DEFAULT_HOST,
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
)


async def test_config_flow_init(hass: HomeAssistant) -> None:
    """Test the initial form is shown."""

    result = await hass.config_entries.flow.async_init(DOMAIN, context={"source": SOURCE_USER})

    assert result["type"] == FlowResultType.FORM
    assert result["step_id"] == "user"
    assert result["errors"] == {}


async def test_config_flow_success(hass: HomeAssistant) -> None:
    """Test successful config flow."""
    with patch(
        "custom_components.mtec.config_flow.MtecApiClient.async_validate_connection",
        return_value=True,
    ):
        result = await hass.config_entries.flow.async_init(
            DOMAIN,
            context={"source": SOURCE_USER},
            data={
                CONF_HOST: "192.168.1.100",
                CONF_SCAN_INTERVAL: 30,
            },
        )

    assert result["type"] == FlowResultType.CREATE_ENTRY
    assert result["title"] == "M-TEC (192.168.1.100)"
    assert result["data"][CONF_HOST] == "192.168.1.100"
    assert result["data"][CONF_SCAN_INTERVAL] == 30


async def test_config_flow_cannot_connect(hass: HomeAssistant) -> None:
    """Test config flow with connection error."""
    with patch(
        "custom_components.mtec.config_flow.MtecApiClient.async_validate_connection",
        return_value=False,
    ):
        result = await hass.config_entries.flow.async_init(
            DOMAIN,
            context={"source": SOURCE_USER},
            data={
                CONF_HOST: "192.168.1.100",
                CONF_SCAN_INTERVAL: 30,
            },
        )

    assert result["type"] == FlowResultType.FORM
    assert result["errors"]["base"] == "cannot_connect"


async def test_config_flow_duplicate(hass: HomeAssistant) -> None:
    """Test config flow with duplicate entry."""
    # Create an existing entry first

    entry = hass.config_entries.async_entry_for_domain_unique_id(DOMAIN, "192.168.1.100")
    if entry is None:
        # Mock existing entry
        with patch(
            "custom_components.mtec.config_flow.MtecApiClient.async_validate_connection",
            return_value=True,
        ):
            result = await hass.config_entries.flow.async_init(
                DOMAIN,
                context={"source": SOURCE_USER},
                data={
                    CONF_HOST: "192.168.1.100",
                    CONF_SCAN_INTERVAL: 30,
                },
            )
        assert result["type"] == FlowResultType.CREATE_ENTRY

        # Try to create duplicate
        with patch(
            "custom_components.mtec.config_flow.MtecApiClient.async_validate_connection",
            return_value=True,
        ):
            result = await hass.config_entries.flow.async_init(
                DOMAIN,
                context={"source": SOURCE_USER},
                data={
                    CONF_HOST: "192.168.1.100",
                    CONF_SCAN_INTERVAL: 30,
                },
            )

        assert result["type"] == FlowResultType.ABORT
        assert result["reason"] == "already_configured"


async def test_options_flow(hass: HomeAssistant) -> None:
    """Test options flow."""
    # First create an entry
    with (
        patch(
            "custom_components.mtec.config_flow.MtecApiClient.async_validate_connection",
            return_value=True,
        ),
        patch(
            "custom_components.mtec.api.MtecApiClient.async_probe_available_keys",
            return_value={"outdoor_temp"},
        ),
        patch(
            "custom_components.mtec.api.MtecApiClient.async_read_device_info",
            return_value={},
        ),
        patch(
            "custom_components.mtec.coordinator.MtecDataCoordinator._async_update_data",
            return_value={"outdoor_temp": 15.5},
        ),
    ):
        result = await hass.config_entries.flow.async_init(
            DOMAIN,
            context={"source": SOURCE_USER},
            data={
                CONF_HOST: "192.168.1.100",
                CONF_SCAN_INTERVAL: 30,
            },
        )

    assert result["type"] == FlowResultType.CREATE_ENTRY
    entry = result["result"]

    # Now test options flow
    result = await hass.config_entries.options.async_init(entry.entry_id)

    assert result["type"] == FlowResultType.FORM
    assert result["step_id"] == "init"

    # Submit new options
    result = await hass.config_entries.options.async_configure(
        result["flow_id"],
        user_input={CONF_SCAN_INTERVAL: 60},
    )

    assert result["type"] == FlowResultType.CREATE_ENTRY
    assert result["data"][CONF_SCAN_INTERVAL] == 60


async def test_reconfigure_flow(hass: HomeAssistant) -> None:
    """Test reconfigure flow for changing host."""
    # First create an entry
    with (
        patch(
            "custom_components.mtec.config_flow.MtecApiClient.async_validate_connection",
            return_value=True,
        ),
        patch(
            "custom_components.mtec.api.MtecApiClient.async_probe_available_keys",
            return_value={"outdoor_temp"},
        ),
        patch(
            "custom_components.mtec.api.MtecApiClient.async_read_device_info",
            return_value={},
        ),
        patch(
            "custom_components.mtec.coordinator.MtecDataCoordinator._async_update_data",
            return_value={"outdoor_temp": 15.5},
        ),
    ):
        result = await hass.config_entries.flow.async_init(
            DOMAIN,
            context={"source": SOURCE_USER},
            data={
                CONF_HOST: "192.168.1.100",
                CONF_SCAN_INTERVAL: 30,
            },
        )

    assert result["type"] == FlowResultType.CREATE_ENTRY
    entry = result["result"]

    # Now test reconfigure flow
    with patch(
        "custom_components.mtec.config_flow.MtecApiClient.async_validate_connection",
        return_value=True,
    ):
        result = await hass.config_entries.flow.async_init(
            DOMAIN,
            context={
                "source": SOURCE_RECONFIGURE,
                "entry_id": entry.entry_id,
            },
        )

    assert result["type"] == FlowResultType.FORM
    assert result["step_id"] == "reconfigure"

    # Submit new host
    with patch(
        "custom_components.mtec.config_flow.MtecApiClient.async_validate_connection",
        return_value=True,
    ):
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            user_input={CONF_HOST: "192.168.1.200"},
        )

    assert result["type"] == FlowResultType.ABORT
    assert result["reason"] == "reconfigure_successful"


async def test_reconfigure_flow_cannot_connect(hass: HomeAssistant) -> None:
    """Test reconfigure flow with connection error."""
    # First create an entry
    with (
        patch(
            "custom_components.mtec.config_flow.MtecApiClient.async_validate_connection",
            return_value=True,
        ),
        patch(
            "custom_components.mtec.api.MtecApiClient.async_probe_available_keys",
            return_value={"outdoor_temp"},
        ),
        patch(
            "custom_components.mtec.api.MtecApiClient.async_read_device_info",
            return_value={},
        ),
        patch(
            "custom_components.mtec.coordinator.MtecDataCoordinator._async_update_data",
            return_value={"outdoor_temp": 15.5},
        ),
    ):
        result = await hass.config_entries.flow.async_init(
            DOMAIN,
            context={"source": SOURCE_USER},
            data={
                CONF_HOST: "192.168.1.100",
                CONF_SCAN_INTERVAL: 30,
            },
        )

    assert result["type"] == FlowResultType.CREATE_ENTRY
    entry = result["result"]

    # Test reconfigure with bad connection
    with patch(
        "custom_components.mtec.config_flow.MtecApiClient.async_validate_connection",
        return_value=False,
    ):
        result = await hass.config_entries.flow.async_init(
            DOMAIN,
            context={
                "source": SOURCE_RECONFIGURE,
                "entry_id": entry.entry_id,
            },
        )

    assert result["type"] == FlowResultType.FORM

    # Submit with invalid host
    with patch(
        "custom_components.mtec.config_flow.MtecApiClient.async_validate_connection",
        return_value=False,
    ):
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            user_input={CONF_HOST: "192.168.1.300"},
        )

    assert result["type"] == FlowResultType.FORM
    assert result["errors"]["base"] == "cannot_connect"


async def test_default_values_in_form(hass: HomeAssistant) -> None:
    """Test that default values are shown in the form."""
    from custom_components.mtec.config_flow import DATA_SCHEMA

    # Find defaults by iterating schema keys (vol.Required/vol.Optional objects)
    defaults = {}
    for key in DATA_SCHEMA.schema:
        if hasattr(key, "default") and key.default is not vol.UNDEFINED:
            defaults[str(key)] = key.default()

    assert defaults[CONF_HOST] == DEFAULT_HOST
    assert defaults[CONF_SCAN_INTERVAL] == DEFAULT_SCAN_INTERVAL
