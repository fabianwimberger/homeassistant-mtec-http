"""Sensor platform for M-TEC Heat Pump."""

from __future__ import annotations

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import (
    HEATPUMP_STATE_OPTIONS,
    HOT_WATER_MODE_OPTIONS,
    SENSOR_DESCRIPTIONS,
    SG_READY_MODE_OPTIONS,
    SYSTEM_OPERATING_MODE_OPTIONS,
    MtecSensorEntityDescription,
)
from .coordinator import MtecDataCoordinator
from .entity import MtecEntity

# Sensors whose raw int value should be mapped to a human-readable string
_ENUM_SENSORS: dict[str, dict[int, str]] = {
    "heatpump_state": HEATPUMP_STATE_OPTIONS,  # type: ignore[dict-item]  # IntEnum key
    "system_operating_mode": SYSTEM_OPERATING_MODE_OPTIONS,  # type: ignore[dict-item]  # IntEnum key
    "hot_water_mode": HOT_WATER_MODE_OPTIONS,  # type: ignore[dict-item]  # IntEnum key
    "sg_ready_mode": SG_READY_MODE_OPTIONS,  # type: ignore[dict-item]  # IntEnum key
}


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up M-TEC sensors."""
    coordinator: MtecDataCoordinator = entry.runtime_data
    available = coordinator.client.available_keys
    async_add_entities(
        MtecSensor(coordinator, desc) for desc in SENSOR_DESCRIPTIONS if desc.mtec_key in available
    )


class MtecSensor(MtecEntity, SensorEntity):
    """M-TEC sensor entity."""

    entity_description: MtecSensorEntityDescription

    def __init__(
        self,
        coordinator: MtecDataCoordinator,
        description: MtecSensorEntityDescription,
    ) -> None:
        super().__init__(coordinator)
        self.entity_description = description
        self._mtec_key = description.mtec_key
        self._attr_unique_id = f"{coordinator.client.host}_{description.key}"
        self._enum_map = _ENUM_SENSORS.get(description.key)

    @property
    def native_value(self) -> float | int | str | None:
        """Return the sensor value."""
        if self.coordinator.data is None:
            return None
        raw = self.coordinator.data.get(self.entity_description.mtec_key)
        if raw is None:
            return None
        if self._enum_map:
            return self._enum_map.get(int(raw), f"Unknown ({raw})")
        return float(raw) if isinstance(raw, (int, float)) else None
