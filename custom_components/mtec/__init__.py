"""M-TEC Heat Pump integration."""
from __future__ import annotations

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import MtecApiClient
from .const import (
    CONF_HOST,
    CONF_SCAN_INTERVAL,
    DEFAULT_SCAN_INTERVAL,
    DEVICE_INFO_SIGNALS,
    DOMAIN,
    PLATFORMS,
)
from .coordinator import MtecDataCoordinator

_LOGGER = logging.getLogger(__name__)

type MtecConfigEntry = ConfigEntry[MtecDataCoordinator]


async def async_setup_entry(hass: HomeAssistant, entry: MtecConfigEntry) -> bool:
    """Set up M-TEC Heat Pump from a config entry."""
    host = entry.data[CONF_HOST]
    scan_interval = entry.options.get(
        CONF_SCAN_INTERVAL,
        entry.data.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL),
    )

    session = async_get_clientsession(hass)
    client = MtecApiClient(host, session)

    # Probe which signals are available on this unit
    await client.async_probe_available_keys()

    # Read device info (firmware, serial) once
    device_info = await client.async_read_device_info(DEVICE_INFO_SIGNALS)

    coordinator = MtecDataCoordinator(hass, client, scan_interval, device_info)

    await coordinator.async_config_entry_first_refresh()

    entry.runtime_data = coordinator
    entry.async_on_unload(entry.add_update_listener(_async_update_listener))

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def _async_update_listener(hass: HomeAssistant, entry: MtecConfigEntry) -> None:
    """Reload the integration when options change."""
    await hass.config_entries.async_reload(entry.entry_id)


async def async_unload_entry(hass: HomeAssistant, entry: MtecConfigEntry) -> bool:
    """Unload a config entry."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
