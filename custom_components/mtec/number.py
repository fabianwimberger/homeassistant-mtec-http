"""Number platform for M-TEC Heat Pump."""

from __future__ import annotations

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .api import MtecApiError
from .const import NUMBER_DESCRIPTIONS, MtecNumberEntityDescription
from .coordinator import MtecDataCoordinator
from .entity import MtecEntity

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up M-TEC number entities."""
    coordinator: MtecDataCoordinator = entry.runtime_data
    async_add_entities(MtecNumber(coordinator, desc) for desc in NUMBER_DESCRIPTIONS)


class MtecNumber(MtecEntity):
    """M-TEC number entity for settable values."""

    entity_description: MtecNumberEntityDescription

    def __init__(
        self,
        coordinator: MtecDataCoordinator,
        description: MtecNumberEntityDescription,
    ) -> None:
        super().__init__(coordinator)
        self.entity_description = description
        self._mtec_key = description.mtec_key
        self._attr_unique_id = f"{coordinator.client.host}_{description.key}_number"

    @property
    def native_value(self) -> float | None:
        """Return the current value."""
        if self.coordinator.data is None:
            return None
        value = self.coordinator.data.get(self.entity_description.mtec_key)
        return float(value) if isinstance(value, (int, float)) else None

    async def async_set_native_value(self, value: float) -> None:
        """Set the value on the heat pump."""
        try:
            await self.coordinator.client.async_write_value(self.entity_description.mtec_key, value)
        except MtecApiError as err:
            _LOGGER.error("Failed to set %s: %s", self.entity_description.key, err)
            return
        await self.coordinator.async_request_refresh()
