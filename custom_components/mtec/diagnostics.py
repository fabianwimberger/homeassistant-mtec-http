"""Diagnostics support for M-TEC Heat Pump."""

from __future__ import annotations

from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import CONF_HOST
from .coordinator import MtecDataCoordinator


async def async_get_config_entry_diagnostics(
    hass: HomeAssistant, entry: ConfigEntry
) -> dict[str, Any]:
    """Return diagnostics for a config entry."""
    coordinator: MtecDataCoordinator = entry.runtime_data

    return {
        "config": {
            "host": entry.data.get(CONF_HOST, "unknown"),
            "scan_interval": coordinator.update_interval.total_seconds()
            if coordinator.update_interval
            else None,
        },
        "last_update_success": coordinator.last_update_success,
        "data": coordinator.data if coordinator.data else {},
    }
