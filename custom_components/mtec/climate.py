"""Climate platform for M-TEC Heat Pump."""

from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.climate import (
    ClimateEntity,
    ClimateEntityFeature,
    HVACMode,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import ATTR_TEMPERATURE, UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .api import MtecApiError
from .const import MAX_HEAT_CIRCUITS, HeatCircuitMode
from .coordinator import MtecDataCoordinator
from .entity import MtecEntity

_LOGGER = logging.getLogger(__name__)

# Map M-TEC heat circuit modes to HVAC modes
# Modbus doc: 0=Standby, 1=Timer, 2=Day, 3=Night, 4=Vacation, 5=Party, 8=Extern
_MODE_TO_HVAC: dict[int, HVACMode] = {
    HeatCircuitMode.STANDBY: HVACMode.OFF,
    HeatCircuitMode.TIMER: HVACMode.AUTO,
    HeatCircuitMode.DAY: HVACMode.HEAT,
    HeatCircuitMode.NIGHT: HVACMode.HEAT,
    HeatCircuitMode.VACATION: HVACMode.AUTO,
    HeatCircuitMode.PARTY: HVACMode.HEAT,
    HeatCircuitMode.EXTERN: HVACMode.AUTO,
}

# Map HVAC modes back to M-TEC modes
_HVAC_TO_MODE: dict[HVACMode, int] = {
    HVACMode.OFF: HeatCircuitMode.STANDBY,
    HVACMode.AUTO: HeatCircuitMode.TIMER,
    HVACMode.HEAT: HeatCircuitMode.DAY,
}

# Preset modes map to the M-TEC-specific modes beyond the basic HVAC modes
PRESET_NONE = "none"
PRESET_DAY = "Day"
PRESET_NIGHT = "Night"
PRESET_VACATION = "Vacation"
PRESET_PARTY = "Party"

# Map M-TEC mode to preset
_MODE_TO_PRESET: dict[int, str] = {
    HeatCircuitMode.STANDBY: PRESET_NONE,
    HeatCircuitMode.TIMER: PRESET_NONE,
    HeatCircuitMode.DAY: PRESET_DAY,
    HeatCircuitMode.NIGHT: PRESET_NIGHT,
    HeatCircuitMode.VACATION: PRESET_VACATION,
    HeatCircuitMode.PARTY: PRESET_PARTY,
    HeatCircuitMode.EXTERN: PRESET_NONE,
}


CLIMATE_CIRCUITS = [
    {
        "circuit": i,
        "mode_key": f"hc{i}_mode",
        "room_temp_key": f"hc{i}_room_temp",
        "room_set_temp_key": f"hc{i}_room_set_temp",
        "day_temp_key": f"hc{i}_day_temp",
        "night_temp_key": f"hc{i}_night_temp",
        "translation_key": "hc_climate",
    }
    for i in range(MAX_HEAT_CIRCUITS)
]


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up M-TEC climate entities."""
    coordinator: MtecDataCoordinator = entry.runtime_data
    available = coordinator.client.available_keys
    async_add_entities(
        MtecClimate(coordinator, circuit)
        for circuit in CLIMATE_CIRCUITS
        if circuit["mode_key"] in available
    )


class MtecClimate(MtecEntity, ClimateEntity):
    """M-TEC climate entity for a heating circuit."""

    _attr_temperature_unit = UnitOfTemperature.CELSIUS
    _attr_hvac_modes = [HVACMode.OFF, HVACMode.AUTO, HVACMode.HEAT]
    _attr_supported_features = (
        ClimateEntityFeature.TARGET_TEMPERATURE
        | ClimateEntityFeature.PRESET_MODE
        | ClimateEntityFeature.TURN_ON
        | ClimateEntityFeature.TURN_OFF
    )
    _attr_preset_modes = [PRESET_NONE, PRESET_DAY, PRESET_NIGHT, PRESET_VACATION, PRESET_PARTY]
    _attr_target_temperature_step = 0.5
    _attr_min_temp = 10.0
    _attr_max_temp = 30.0
    _enable_turn_on_off_backwards_compat = False

    def __init__(
        self,
        coordinator: MtecDataCoordinator,
        circuit: dict[str, Any],
    ) -> None:
        super().__init__(coordinator)
        self._circuit = circuit["circuit"]
        self._mode_key = circuit["mode_key"]
        self._room_temp_key = circuit["room_temp_key"]
        self._room_set_temp_key = circuit["room_set_temp_key"]
        self._day_temp_key = circuit["day_temp_key"]
        self._night_temp_key = circuit["night_temp_key"]
        self._mtec_key = circuit["mode_key"]
        self._attr_name = f"HC{self._circuit} heating circuit"
        self._attr_unique_id = f"{coordinator.client.host}_hc{self._circuit}_climate"
        self._attr_icon = "mdi:radiator"

    def _raw_mode(self) -> int | None:
        """Return the raw M-TEC operating mode integer."""
        if self.coordinator.data is None:
            return None
        raw = self.coordinator.data.get(self._mode_key)
        if raw is None:
            return None
        return int(raw)

    @property
    def hvac_mode(self) -> HVACMode | None:
        """Return the current HVAC mode."""
        raw = self._raw_mode()
        if raw is None:
            return None
        return _MODE_TO_HVAC.get(raw, HVACMode.AUTO)

    @property
    def current_temperature(self) -> float | None:
        """Return the current room temperature."""
        if self.coordinator.data is None:
            return None
        value = self.coordinator.data.get(self._room_temp_key)
        return float(value) if isinstance(value, (int, float)) else None

    @property
    def target_temperature(self) -> float | None:
        """Return the target temperature (selected set temp from the pump)."""
        if self.coordinator.data is None:
            return None
        value = self.coordinator.data.get(self._room_set_temp_key)
        return float(value) if isinstance(value, (int, float)) else None

    @property
    def preset_mode(self) -> str | None:
        """Return the current preset based on M-TEC mode."""
        raw = self._raw_mode()
        if raw is None:
            return None
        return _MODE_TO_PRESET.get(raw, PRESET_NONE)

    async def async_set_hvac_mode(self, hvac_mode: HVACMode) -> None:
        """Set the HVAC mode."""
        mtec_mode = _HVAC_TO_MODE.get(hvac_mode)
        if mtec_mode is None:
            _LOGGER.error("Unsupported HVAC mode: %s", hvac_mode)
            return
        try:
            await self.coordinator.client.async_write_value(self._mode_key, float(mtec_mode))
        except MtecApiError as err:
            _LOGGER.error("Failed to set HC%d mode: %s", self._circuit, err)
            return
        await self.coordinator.async_request_refresh()

    async def async_turn_on(self) -> None:
        """Turn on: set circuit to Timer (Auto) mode."""
        await self.async_set_hvac_mode(HVACMode.AUTO)

    async def async_turn_off(self) -> None:
        """Turn off: set circuit to Standby mode."""
        await self.async_set_hvac_mode(HVACMode.OFF)

    async def async_set_temperature(self, **kwargs: Any) -> None:
        """Set the target temperature (writes to the day temp setpoint)."""
        temp = kwargs.get(ATTR_TEMPERATURE)
        if temp is None:
            return
        # Write to day or night temp depending on current mode
        raw = self._raw_mode()
        key = self._night_temp_key if raw == HeatCircuitMode.NIGHT else self._day_temp_key
        try:
            await self.coordinator.client.async_write_value(key, float(temp))
        except MtecApiError as err:
            _LOGGER.error("Failed to set HC%d temperature: %s", self._circuit, err)
            return
        await self.coordinator.async_request_refresh()

    async def async_set_preset_mode(self, preset_mode: str) -> None:
        """Set the preset mode."""
        preset_to_mode = {
            PRESET_NONE: HeatCircuitMode.TIMER,
            PRESET_DAY: HeatCircuitMode.DAY,
            PRESET_NIGHT: HeatCircuitMode.NIGHT,
            PRESET_VACATION: HeatCircuitMode.VACATION,
            PRESET_PARTY: HeatCircuitMode.PARTY,
        }
        mtec_mode = preset_to_mode.get(preset_mode)
        if mtec_mode is None:
            _LOGGER.error("Unknown preset: %s", preset_mode)
            return
        try:
            await self.coordinator.client.async_write_value(self._mode_key, float(mtec_mode))
        except MtecApiError as err:
            _LOGGER.error("Failed to set HC%d preset: %s", self._circuit, err)
            return
        await self.coordinator.async_request_refresh()
