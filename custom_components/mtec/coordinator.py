"""Data update coordinator for M-TEC Heat Pump."""
from __future__ import annotations

from datetime import timedelta
import logging

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import MtecApiClient, MtecApiError
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


class MtecDataCoordinator(DataUpdateCoordinator[dict[str, float | int]]):
    """Coordinator to manage fetching M-TEC data."""

    def __init__(
        self,
        hass: HomeAssistant,
        client: MtecApiClient,
        scan_interval: int,
        device_info: dict[str, str] | None = None,
    ) -> None:
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=scan_interval),
        )
        self.client = client
        self.device_info_data = device_info or {}

    async def _async_update_data(self) -> dict[str, float | int]:
        """Fetch data from the heat pump."""
        try:
            return await self.client.async_read_values()
        except MtecApiError as err:
            raise UpdateFailed(f"Error fetching data: {err}") from err
