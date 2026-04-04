"""Base entity for M-TEC Heat Pump."""
from __future__ import annotations

from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import MtecDataCoordinator


class MtecEntity(CoordinatorEntity[MtecDataCoordinator]):
    """Base entity for M-TEC."""

    _attr_has_entity_name = True
    _mtec_key: str = ""

    def __init__(self, coordinator: MtecDataCoordinator) -> None:
        super().__init__(coordinator)
        info = coordinator.device_info_data
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, coordinator.client.host)},
            name="M-TEC Heat Pump",
            manufacturer="M-TEC",
            model="Heat Pump",
            sw_version=info.get("firmware_version"),
            serial_number=info.get("serial_number"),
        )

    @property
    def available(self) -> bool:
        """Return True if the entity's key is present in coordinator data."""
        if not super().available:
            return False
        if self.coordinator.data is None:
            return False
        if self._mtec_key:
            return self._mtec_key in self.coordinator.data
        return True
