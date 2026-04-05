"""Binary sensor platform for M-TEC Heat Pump."""

from __future__ import annotations

from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import BINARY_SENSOR_DESCRIPTIONS, MtecBinarySensorEntityDescription
from .coordinator import MtecDataCoordinator
from .entity import MtecEntity


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up M-TEC binary sensors."""
    coordinator: MtecDataCoordinator = entry.runtime_data
    available = coordinator.client.available_keys
    async_add_entities(
        MtecBinarySensor(coordinator, desc)
        for desc in BINARY_SENSOR_DESCRIPTIONS
        if desc.mtec_key in available
    )


class MtecBinarySensor(MtecEntity, BinarySensorEntity):
    """M-TEC binary sensor entity."""

    entity_description: MtecBinarySensorEntityDescription

    def __init__(
        self,
        coordinator: MtecDataCoordinator,
        description: MtecBinarySensorEntityDescription,
    ) -> None:
        super().__init__(coordinator)
        self.entity_description = description
        self._mtec_key = description.mtec_key
        self._attr_unique_id = f"{coordinator.client.host}_{description.key}_binary"

    @property
    def is_on(self) -> bool | None:
        """Return true if the binary sensor is on."""
        if self.coordinator.data is None:
            return None
        raw = self.coordinator.data.get(self.entity_description.mtec_key)
        if raw is None:
            return None
        return bool(raw)
