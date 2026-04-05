"""Diagnostics support for M-TEC Heat Pump."""

from __future__ import annotations

from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import CONF_HOST, SIGNAL_MAP
from .coordinator import MtecDataCoordinator


async def async_get_config_entry_diagnostics(
    hass: HomeAssistant, entry: ConfigEntry
) -> dict[str, Any]:
    """Return diagnostics for a config entry."""
    coordinator: MtecDataCoordinator = entry.runtime_data
    available = coordinator.client.available_keys
    all_keys = set(SIGNAL_MAP.keys())

    return {
        "config": {
            "host": entry.data.get(CONF_HOST, "unknown"),
            "scan_interval": coordinator.update_interval.total_seconds()
            if coordinator.update_interval
            else None,
        },
        "last_update_success": coordinator.last_update_success,
        "signals": {
            "total": len(all_keys),
            "available": sorted(available),
            "unavailable": sorted(all_keys - available),
        },
        "data": coordinator.data if coordinator.data else {},
    }
