"""Select platform for M-TEC Heat Pump."""
from __future__ import annotations

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .api import MtecApiError
from .const import DOMAIN, SELECT_DESCRIPTIONS, MtecSelectEntityDescription
from .coordinator import MtecDataCoordinator
from .entity import MtecEntity

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up M-TEC select entities."""
    coordinator: MtecDataCoordinator = entry.runtime_data
    async_add_entities(
        MtecSelect(coordinator, desc) for desc in SELECT_DESCRIPTIONS
    )


class MtecSelect(MtecEntity):
    """M-TEC select entity for operating modes."""

    entity_description: MtecSelectEntityDescription

    def __init__(
        self,
        coordinator: MtecDataCoordinator,
        description: MtecSelectEntityDescription,
    ) -> None:
        super().__init__(coordinator)
        self.entity_description = description
        self._mtec_key = description.mtec_key
        self._attr_unique_id = f"{coordinator.client.host}_{description.key}_select"
        self._reverse_map = {v: k for k, v in description.options_map.items()}

    @property
    def current_option(self) -> str | None:
        """Return the current mode."""
        if self.coordinator.data is None:
            return None
        raw = self.coordinator.data.get(self.entity_description.mtec_key)
        if raw is None:
            return None
        return self.entity_description.options_map.get(int(raw))

    async def async_select_option(self, option: str) -> None:
        """Set the operating mode."""
        raw_value = self._reverse_map.get(option)
        if raw_value is None:
            _LOGGER.error("Unknown option %s for %s", option, self.entity_description.key)
            return
        try:
            await self.coordinator.client.async_write_value(
                self.entity_description.mtec_key, float(raw_value)
            )
        except MtecApiError as err:
            _LOGGER.error("Failed to set %s: %s", self.entity_description.key, err)
            return
        await self.coordinator.async_request_refresh()
