"""Constants for the M-TEC Heat Pump integration."""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import IntEnum
from collections.abc import Callable

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntityDescription,
)
from homeassistant.components.number import NumberDeviceClass, NumberEntityDescription
from homeassistant.components.select import SelectEntityDescription
from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.const import (
    PERCENTAGE,
    UnitOfEnergy,
    UnitOfPower,
    UnitOfPressure,
    UnitOfTemperature,
    UnitOfTime,
)

DOMAIN = "mtec"
CONF_HOST = "host"
CONF_SCAN_INTERVAL = "scan_interval"
DEFAULT_HOST = "192.168.1.100"
DEFAULT_SCAN_INTERVAL = 15

API_ENDPOINT = "/var/readWriteVars"

# --- Signals read once at setup for device info ---

DEVICE_INFO_SIGNALS: dict[str, str] = {
    "firmware_version": "APPL.CtrlAppl.sParam.param.applVersion",
    "serial_number": "APPL.CtrlAppl.sParam.param.systemSerialNumber",
}


# --- Signal name mappings (key -> M-TEC API signal name) ---

SIGNAL_MAP: dict[str, str] = {
    # System
    "system_operating_mode": "APPL.CtrlAppl.sParam.param.operatingMode",
    "outdoor_temp": "APPL.CtrlAppl.sParam.outdoorTemp.values.actValue",
    # Heat pump
    "heating_power": "APPL.CtrlAppl.sParam.heatpump[0].HeatMeter.values.power",
    "electrical_power": "APPL.CtrlAppl.sParam.heatpump[0].ElectricEnergyMeter.values.power",
    "heatpump_state": "APPL.CtrlAppl.sParam.heatpump[0].values.heatpumpState",
    "temp_vaporizer": "APPL.CtrlAppl.sParam.heatpump[0].OverHeatCtrl.values.tempVap",
    "temp_condenser": "APPL.CtrlAppl.sParam.heatpump[0].OverHeatCtrl.values.tempCond",
    "temp_heat_flow": "APPL.CtrlAppl.sParam.heatpump[0].TempHeatFlow.values.actValue",
    "temp_heat_return": "APPL.CtrlAppl.sParam.heatpump[0].TempHeatReflux.values.actValue",
    "temp_source_in": "APPL.CtrlAppl.sParam.heatpump[0].TempSourceIn.values.actValue",
    "temp_source_out": "APPL.CtrlAppl.sParam.heatpump[0].TempSourceOut.values.actValue",
    "circ_pump": "APPL.CtrlAppl.sParam.heatpump[0].CircPump.values.setValueScaled",
    "compressor": "APPL.CtrlAppl.sParam.heatpump[0].Compressor.values.setValueScaled",
    "fan": "APPL.CtrlAppl.sParam.heatpump[0].Source.values.setValueScaled",
    "mass_flow": "APPL.CtrlAppl.sParam.heatpump[0].HeatMeter.values.massFlow",
    "operating_hours": "APPL.CtrlAppl.sStatisticalData.heatpump[0].consumption.operatingtime",
    "total_heating_energy": "APPL.CtrlAppl.sStatisticalData.heatpump[0].consumption.energy",
    "total_electrical_energy": "APPL.CtrlAppl.sStatisticalData.heatpump[0].consumption.electricalenergy",
    "temp_compressor_in": "APPL.CtrlAppl.sParam.heatpump[0].TempCompressorIn.values.actValue",
    "temp_compressor_out": "APPL.CtrlAppl.sParam.heatpump[0].TempCompressorOut.values.actValue",
    "superheat_actual": "APPL.CtrlAppl.sParam.heatpump[0].OverHeatCtrl.values.actOH",
    "superheat_set": "APPL.CtrlAppl.sParam.heatpump[0].OverHeatCtrl.values.setOH",
    "low_pressure": "APPL.CtrlAppl.sParam.heatpump[0].LowPressure.values.actValue",
    "high_pressure": "APPL.CtrlAppl.sParam.heatpump[0].HighPressure.values.actValue",
    "cop": "APPL.CtrlAppl.sParam.heatpump[0].values.COP",
    # Buffer tank
    "buffer_top_temp": "APPL.CtrlAppl.sParam.bufferTank[0].topTemp.values.actValue",
    "buffer_mid_temp": "APPL.CtrlAppl.sParam.bufferTank[0].midTemp.values.actValue",
    "buffer_set_temp": "APPL.CtrlAppl.sParam.bufferTank[0].values.setTemp",
    "buffer_heat_request": "APPL.CtrlAppl.sParam.bufferTank[0].values.heatRequestTop",
    "buffer_cool_request": "APPL.CtrlAppl.sParam.bufferTank[0].values.coolRequestBot",
    "buffer_switch_valve": "APPL.CtrlAppl.sParam.bufferTank[0].switchValveInvLoad.values.actPosition",
    # Hot water tank
    "hot_water_top_temp": "APPL.CtrlAppl.sParam.hotWaterTank[0].topTemp.values.actValue",
    "hot_water_target_temp": "APPL.CtrlAppl.sParam.hotWaterTank[0].param.normalSetTempMax.value",
    "hot_water_mode": "APPL.CtrlAppl.sParam.hotWaterTank[0].param.operatingMode",
    "hot_water_heat_request": "APPL.CtrlAppl.sParam.hotWaterTank[0].values.heatRequestTop",
    "hot_water_pump": "APPL.CtrlAppl.sParam.hotWaterTank[0].pump.values.setValueB",
    "hot_water_circ_pump": "APPL.CtrlAppl.sParam.hotWaterTank[0].circPump.pump.values.setValueB",
    "hot_water_circ_temp": "APPL.CtrlAppl.sParam.hotWaterTank[0].circTemp.values.actValue",
    # Heat circuit 0
    "hc0_mode": "APPL.CtrlAppl.sParam.heatCircuit[0].param.operatingMode",
    "hc0_room_temp": "APPL.CtrlAppl.sParam.heatCircuit[0].tempRoom.values.actValue",
    "hc0_room_set_temp": "APPL.CtrlAppl.sParam.heatCircuit[0].values.selectedSetTemp",
    "hc0_flow_actual_temp": "APPL.CtrlAppl.sParam.heatCircuit[0].heatCircuitMixer.flowTemp.values.actValue",
    "hc0_flow_set_temp": "APPL.CtrlAppl.sParam.heatCircuit[0].values.flowSetTemp",
    "hc0_return_temp": "APPL.CtrlAppl.sParam.heatCircuit[0].tempReflux.values.actValue",
    "hc0_heat_request": "APPL.CtrlAppl.sParam.heatCircuit[0].values.heatRequest",
    "hc0_cool_request": "APPL.CtrlAppl.sParam.heatCircuit[0].values.coolRequest",
    "hc0_day_temp": "APPL.CtrlAppl.sParam.heatCircuit[0].param.normalSetTemp",
    "hc0_night_temp": "APPL.CtrlAppl.sParam.heatCircuit[0].param.reducedSetTemp",
    "hc0_offset_temp": "APPL.CtrlAppl.sParam.heatCircuit[0].param.offsetRoomTemp",
    "hc0_humidity": "APPL.CtrlAppl.sParam.heatCircuit[0].humidityRoom.values.actValue",
    "hc0_mixer": "APPL.CtrlAppl.sParam.heatCircuit[0].heatCircuitMixer.mixer.values.setValueScaled",
    "hc0_pump": "APPL.CtrlAppl.sParam.heatCircuit[0].pump.values.setValueB",
    # Heat circuit 1
    "hc1_mode": "APPL.CtrlAppl.sParam.heatCircuit[1].param.operatingMode",
    "hc1_room_temp": "APPL.CtrlAppl.sParam.heatCircuit[1].tempRoom.values.actValue",
    "hc1_room_set_temp": "APPL.CtrlAppl.sParam.heatCircuit[1].values.selectedSetTemp",
    "hc1_flow_actual_temp": "APPL.CtrlAppl.sParam.heatCircuit[1].heatCircuitMixer.flowTemp.values.actValue",
    "hc1_flow_set_temp": "APPL.CtrlAppl.sParam.heatCircuit[1].values.flowSetTemp",
    "hc1_return_temp": "APPL.CtrlAppl.sParam.heatCircuit[1].tempReflux.values.actValue",
    "hc1_heat_request": "APPL.CtrlAppl.sParam.heatCircuit[1].values.heatRequest",
    "hc1_cool_request": "APPL.CtrlAppl.sParam.heatCircuit[1].values.coolRequest",
    "hc1_day_temp": "APPL.CtrlAppl.sParam.heatCircuit[1].param.normalSetTemp",
    "hc1_night_temp": "APPL.CtrlAppl.sParam.heatCircuit[1].param.reducedSetTemp",
    "hc1_offset_temp": "APPL.CtrlAppl.sParam.heatCircuit[1].param.offsetRoomTemp",
    "hc1_humidity": "APPL.CtrlAppl.sParam.heatCircuit[1].humidityRoom.values.actValue",
    "hc1_mixer": "APPL.CtrlAppl.sParam.heatCircuit[1].heatCircuitMixer.mixer.values.setValueScaled",
    "hc1_pump": "APPL.CtrlAppl.sParam.heatCircuit[1].pump.values.setValueB",
    # Solar
    "solar_collector_temp": "APPL.CtrlAppl.sParam.solarCircuit[0].collectorTemp.values.actValue",
    # Photovoltaics / Smart Grid
    "pv_excess_energy": "APPL.CtrlAppl.sParam.photovoltaics.values.excessEnergyActive",
    "pv_meter_power": "APPL.CtrlAppl.sParam.photovoltaics.ElectricEnergyMeter.values.power",
    "sg_ready_mode": "APPL.CtrlAppl.sParam.smartgrid.values.smartGridReadyOpMode",
    # External / misc
    "ext_heat_source": "APPL.CtrlAppl.sParam.extHeatSource[0].values.setValueB",
    "ext_heat_source_request": "APPL.CtrlAppl.sParam.extHeatSource[0].values.requestExtHeatsource",
    "screed_drying_active": "APPL.CtrlAppl.sParam.screedDrying.values.active",
    # Alarms
    "alarm_id_0": "APPL.CtrlAppl.sParam.values.pendingAlarms.ID0",
    "alarm_id_1": "APPL.CtrlAppl.sParam.values.pendingAlarms.ID1",
    "alarm_id_2": "APPL.CtrlAppl.sParam.values.pendingAlarms.ID2",
    "alarm_id_3": "APPL.CtrlAppl.sParam.values.pendingAlarms.ID3",
    "alarm_id_4": "APPL.CtrlAppl.sParam.values.pendingAlarms.ID4",
}

# Reverse map: API signal name -> key
SIGNAL_MAP_REV = {v: k for k, v in SIGNAL_MAP.items()}


# --- Value conversion functions ---

def conv_temp1(v: float) -> float:
    """Round temperature to 1 decimal."""
    return round(v, 1)


def conv_temp2(v: float) -> float:
    """Round temperature to 2 decimals."""
    return round(v, 2)


def conv_int(v: float) -> int:
    """Truncate to integer."""
    return int(v)


def conv_hours(v: float) -> float:
    """Convert seconds to hours."""
    return round(v / 3600, 2)


def conv_percent(v: float) -> float:
    """Convert 0-1 fraction to percentage."""
    return round(v * 100, 2)


def conv_mass_flow(v: float) -> float:
    """Convert kg/s to kg/h."""
    return round(v * 3600)


def conv_watts_kw(v: float) -> float:
    """Convert watts to kilowatts."""
    return round(v) / 1000


def conv_bar(v: float) -> float:
    """Round pressure to 2 decimals (bar)."""
    return round(v, 2)


def conv_energy(v: float) -> float:
    """Round energy to 1 decimal (kWh)."""
    return round(v, 1)


# Mapping of key -> conversion function
CONVERSIONS: dict[str, Callable[[float], float | int]] = {
    "system_operating_mode": conv_int,
    "outdoor_temp": conv_temp1,
    "heating_power": conv_watts_kw,
    "electrical_power": conv_int,
    "heatpump_state": conv_int,
    "temp_vaporizer": conv_temp2,
    "temp_condenser": conv_temp2,
    "temp_heat_flow": conv_temp1,
    "temp_heat_return": conv_temp1,
    "temp_source_in": conv_temp1,
    "temp_source_out": conv_temp1,
    "circ_pump": conv_percent,
    "compressor": conv_percent,
    "fan": conv_percent,
    "mass_flow": conv_mass_flow,
    "operating_hours": conv_hours,
    "total_heating_energy": conv_energy,
    "total_electrical_energy": conv_energy,
    "temp_compressor_in": conv_temp1,
    "temp_compressor_out": conv_temp1,
    "superheat_actual": conv_temp1,
    "superheat_set": conv_temp1,
    "low_pressure": conv_bar,
    "high_pressure": conv_bar,
    "cop": conv_temp2,
    "buffer_top_temp": conv_temp1,
    "buffer_mid_temp": conv_temp1,
    "buffer_set_temp": conv_temp1,
    "buffer_switch_valve": conv_int,
    "hot_water_top_temp": conv_temp1,
    "hot_water_target_temp": conv_temp1,
    "hot_water_circ_temp": conv_temp1,
    "hot_water_mode": conv_int,
    "hc0_mode": conv_int,
    "hc0_room_temp": conv_temp1,
    "hc0_room_set_temp": conv_temp1,
    "hc0_flow_actual_temp": conv_temp1,
    "hc0_flow_set_temp": conv_temp1,
    "hc0_return_temp": conv_temp1,
    "hc0_heat_request": conv_int,
    "hc0_cool_request": conv_int,
    "hc0_day_temp": conv_temp1,
    "hc0_night_temp": conv_temp1,
    "hc0_offset_temp": conv_temp1,
    "hc0_humidity": conv_int,
    "hc0_mixer": conv_percent,
    "hc1_mode": conv_int,
    "hc1_room_temp": conv_temp1,
    "hc1_room_set_temp": conv_temp1,
    "hc1_flow_actual_temp": conv_temp1,
    "hc1_flow_set_temp": conv_temp1,
    "hc1_return_temp": conv_temp1,
    "hc1_heat_request": conv_int,
    "hc1_cool_request": conv_int,
    "hc1_day_temp": conv_temp1,
    "hc1_night_temp": conv_temp1,
    "hc1_offset_temp": conv_temp1,
    "hc1_humidity": conv_int,
    "hc1_mixer": conv_percent,
    "hc1_pump": conv_int,
    "solar_collector_temp": conv_temp1,
    "pv_meter_power": conv_int,
    "sg_ready_mode": conv_int,
    "ext_heat_source_request": conv_int,
    "alarm_id_0": conv_int,
    "alarm_id_1": conv_int,
    "alarm_id_2": conv_int,
    "alarm_id_3": conv_int,
    "alarm_id_4": conv_int,
}


# --- Operating mode enums (from official Modbus documentation) ---

class SystemOperatingMode(IntEnum):
    """System operating mode.

    From Modbus doc: Setup (-1), Standby (0), Summer (1), AutoHeat (2), AutoCool (3), FullAuto (4)
    """
    STANDBY = 0
    SUMMER = 1
    AUTO_HEAT = 2
    AUTO_COOL = 3
    FULL_AUTO = 4


class HotWaterMode(IntEnum):
    """Hot water tank operating mode.

    From Modbus doc: 0=Off, 1=Time program, 2=Continuous, 3=Forced load
    """
    OFF = 0
    TIME_PROGRAM = 1
    CONTINUOUS = 2
    FORCED_LOAD = 3


class HeatCircuitMode(IntEnum):
    """Heat circuit operating mode.

    From Modbus doc: 0=Standby, 1=Timer, 2=Day, 3=Night, 4=Vacation, 5=Party, 8=Extern
    """
    STANDBY = 0
    TIMER = 1
    DAY = 2
    NIGHT = 3
    VACATION = 4
    PARTY = 5
    EXTERN = 8


class HeatpumpState(IntEnum):
    """Heat pump operational state.

    From Modbus doc: 0=Standby, 1=PreRun, 2=AutomaticHeat, 3=Defrost, 4=AutomaticCool,
                     5=PostRun, 7=SafetyShutdown, 8=Error
    """
    STANDBY = 0
    PRE_RUN = 1
    AUTOMATIC_HEAT = 2
    DEFROST = 3
    AUTOMATIC_COOL = 4
    POST_RUN = 5
    SAFETY_SHUTDOWN = 7
    ERROR = 8


class SGReadyMode(IntEnum):
    """SG Ready operating mode."""
    MODE_1 = 1  # Blocking
    MODE_2 = 2  # Normal
    MODE_3 = 3  # Recommendation to increase
    MODE_4 = 4  # Force on


SYSTEM_OPERATING_MODE_OPTIONS = {
    SystemOperatingMode.STANDBY: "Standby",
    SystemOperatingMode.SUMMER: "Summer",
    SystemOperatingMode.AUTO_HEAT: "Auto Heat",
    SystemOperatingMode.AUTO_COOL: "Auto Cool",
    SystemOperatingMode.FULL_AUTO: "Full Auto",
}

HOT_WATER_MODE_OPTIONS = {
    HotWaterMode.OFF: "Off",
    HotWaterMode.TIME_PROGRAM: "Time Program",
    HotWaterMode.CONTINUOUS: "Continuous",
    HotWaterMode.FORCED_LOAD: "Forced Load",
}

HEAT_CIRCUIT_MODE_OPTIONS = {
    HeatCircuitMode.STANDBY: "Standby",
    HeatCircuitMode.TIMER: "Timer",
    HeatCircuitMode.DAY: "Day",
    HeatCircuitMode.NIGHT: "Night",
    HeatCircuitMode.VACATION: "Vacation",
    HeatCircuitMode.PARTY: "Party",
    HeatCircuitMode.EXTERN: "Extern",
}

HEATPUMP_STATE_OPTIONS = {
    HeatpumpState.STANDBY: "Standby",
    HeatpumpState.PRE_RUN: "Pre-Run",
    HeatpumpState.AUTOMATIC_HEAT: "Heating",
    HeatpumpState.DEFROST: "Defrost",
    HeatpumpState.AUTOMATIC_COOL: "Cooling",
    HeatpumpState.POST_RUN: "Post-Run",
    HeatpumpState.SAFETY_SHUTDOWN: "Safety Shutdown",
    HeatpumpState.ERROR: "Error",
}

SG_READY_MODE_OPTIONS = {
    SGReadyMode.MODE_1: "Blocking",
    SGReadyMode.MODE_2: "Normal",
    SGReadyMode.MODE_3: "Increase",
    SGReadyMode.MODE_4: "Force On",
}


# --- Entity descriptions ---

@dataclass(frozen=True)
class MtecSensorEntityDescription(SensorEntityDescription):
    """Sensor entity description for M-TEC."""
    mtec_key: str = ""


@dataclass(frozen=True)
class MtecBinarySensorEntityDescription(BinarySensorEntityDescription):
    """Binary sensor entity description for M-TEC."""
    mtec_key: str = ""


@dataclass(frozen=True)
class MtecNumberEntityDescription(NumberEntityDescription):
    """Number entity description for M-TEC."""
    mtec_key: str = ""


@dataclass(frozen=True)
class MtecSelectEntityDescription(SelectEntityDescription):
    """Select entity description for M-TEC."""
    mtec_key: str = ""
    options_map: dict[int, str] = field(default_factory=dict)


SENSOR_DESCRIPTIONS: tuple[MtecSensorEntityDescription, ...] = (
    MtecSensorEntityDescription(
        key="outdoor_temp",
        mtec_key="outdoor_temp",
        translation_key="outdoor_temp",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    MtecSensorEntityDescription(
        key="heating_power",
        mtec_key="heating_power",
        translation_key="heating_power",
        native_unit_of_measurement=UnitOfPower.KILO_WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    MtecSensorEntityDescription(
        key="electrical_power",
        mtec_key="electrical_power",
        translation_key="electrical_power",
        native_unit_of_measurement=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    MtecSensorEntityDescription(
        key="heatpump_state",
        mtec_key="heatpump_state",
        translation_key="heatpump_state",
        icon="mdi:heat-pump-outline",
    ),
    MtecSensorEntityDescription(
        key="temp_vaporizer",
        mtec_key="temp_vaporizer",
        translation_key="temp_vaporizer",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    MtecSensorEntityDescription(
        key="temp_condenser",
        mtec_key="temp_condenser",
        translation_key="temp_condenser",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    MtecSensorEntityDescription(
        key="temp_heat_flow",
        mtec_key="temp_heat_flow",
        translation_key="temp_heat_flow",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    MtecSensorEntityDescription(
        key="temp_heat_return",
        mtec_key="temp_heat_return",
        translation_key="temp_heat_return",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    MtecSensorEntityDescription(
        key="temp_source_in",
        mtec_key="temp_source_in",
        translation_key="temp_source_in",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    MtecSensorEntityDescription(
        key="temp_source_out",
        mtec_key="temp_source_out",
        translation_key="temp_source_out",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    MtecSensorEntityDescription(
        key="circ_pump",
        mtec_key="circ_pump",
        translation_key="circ_pump",
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:pump",
    ),
    MtecSensorEntityDescription(
        key="compressor",
        mtec_key="compressor",
        translation_key="compressor",
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:air-conditioner",
    ),
    MtecSensorEntityDescription(
        key="fan",
        mtec_key="fan",
        translation_key="fan",
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:fan",
    ),
    MtecSensorEntityDescription(
        key="mass_flow",
        mtec_key="mass_flow",
        translation_key="mass_flow",
        native_unit_of_measurement="kg/h",
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:water-pump",
    ),
    MtecSensorEntityDescription(
        key="operating_hours",
        mtec_key="operating_hours",
        translation_key="operating_hours",
        native_unit_of_measurement=UnitOfTime.HOURS,
        device_class=SensorDeviceClass.DURATION,
        state_class=SensorStateClass.TOTAL_INCREASING,
        icon="mdi:clock-outline",
    ),
    MtecSensorEntityDescription(
        key="total_heating_energy",
        mtec_key="total_heating_energy",
        translation_key="total_heating_energy",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
    ),
    MtecSensorEntityDescription(
        key="total_electrical_energy",
        mtec_key="total_electrical_energy",
        translation_key="total_electrical_energy",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
    ),
    MtecSensorEntityDescription(
        key="temp_compressor_in",
        mtec_key="temp_compressor_in",
        translation_key="temp_compressor_in",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    MtecSensorEntityDescription(
        key="temp_compressor_out",
        mtec_key="temp_compressor_out",
        translation_key="temp_compressor_out",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    MtecSensorEntityDescription(
        key="superheat_actual",
        mtec_key="superheat_actual",
        translation_key="superheat_actual",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:thermometer-chevron-up",
    ),
    MtecSensorEntityDescription(
        key="superheat_set",
        mtec_key="superheat_set",
        translation_key="superheat_set",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:thermometer-chevron-up",
    ),
    MtecSensorEntityDescription(
        key="low_pressure",
        mtec_key="low_pressure",
        translation_key="low_pressure",
        native_unit_of_measurement=UnitOfPressure.BAR,
        device_class=SensorDeviceClass.PRESSURE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    MtecSensorEntityDescription(
        key="high_pressure",
        mtec_key="high_pressure",
        translation_key="high_pressure",
        native_unit_of_measurement=UnitOfPressure.BAR,
        device_class=SensorDeviceClass.PRESSURE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    MtecSensorEntityDescription(
        key="cop",
        mtec_key="cop",
        translation_key="cop",
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:gauge",
    ),
    # Buffer tank
    MtecSensorEntityDescription(
        key="buffer_top_temp",
        mtec_key="buffer_top_temp",
        translation_key="buffer_top_temp",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    MtecSensorEntityDescription(
        key="buffer_mid_temp",
        mtec_key="buffer_mid_temp",
        translation_key="buffer_mid_temp",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    MtecSensorEntityDescription(
        key="buffer_set_temp",
        mtec_key="buffer_set_temp",
        translation_key="buffer_set_temp",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    MtecSensorEntityDescription(
        key="buffer_switch_valve",
        mtec_key="buffer_switch_valve",
        translation_key="buffer_switch_valve",
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:valve",
    ),
    # Hot water tank
    MtecSensorEntityDescription(
        key="hot_water_top_temp",
        mtec_key="hot_water_top_temp",
        translation_key="hot_water_top_temp",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    MtecSensorEntityDescription(
        key="hot_water_circ_temp",
        mtec_key="hot_water_circ_temp",
        translation_key="hot_water_circ_temp",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    # Heat circuit 0 sensors
    MtecSensorEntityDescription(
        key="hc0_room_temp",
        mtec_key="hc0_room_temp",
        translation_key="hc0_room_temp",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    MtecSensorEntityDescription(
        key="hc0_room_set_temp",
        mtec_key="hc0_room_set_temp",
        translation_key="hc0_room_set_temp",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    MtecSensorEntityDescription(
        key="hc0_flow_actual_temp",
        mtec_key="hc0_flow_actual_temp",
        translation_key="hc0_flow_actual_temp",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    MtecSensorEntityDescription(
        key="hc0_flow_set_temp",
        mtec_key="hc0_flow_set_temp",
        translation_key="hc0_flow_set_temp",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    MtecSensorEntityDescription(
        key="hc0_return_temp",
        mtec_key="hc0_return_temp",
        translation_key="hc0_return_temp",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    MtecSensorEntityDescription(
        key="hc0_heat_request",
        mtec_key="hc0_heat_request",
        translation_key="hc0_heat_request",
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:fire",
    ),
    MtecSensorEntityDescription(
        key="hc0_cool_request",
        mtec_key="hc0_cool_request",
        translation_key="hc0_cool_request",
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:snowflake",
    ),
    MtecSensorEntityDescription(
        key="hc0_humidity",
        mtec_key="hc0_humidity",
        translation_key="hc0_humidity",
        native_unit_of_measurement=PERCENTAGE,
        device_class=SensorDeviceClass.HUMIDITY,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    MtecSensorEntityDescription(
        key="hc0_mixer",
        mtec_key="hc0_mixer",
        translation_key="hc0_mixer",
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:valve",
    ),
    # Heat circuit 1 sensors
    MtecSensorEntityDescription(
        key="hc1_room_temp",
        mtec_key="hc1_room_temp",
        translation_key="hc1_room_temp",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    MtecSensorEntityDescription(
        key="hc1_room_set_temp",
        mtec_key="hc1_room_set_temp",
        translation_key="hc1_room_set_temp",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    MtecSensorEntityDescription(
        key="hc1_flow_actual_temp",
        mtec_key="hc1_flow_actual_temp",
        translation_key="hc1_flow_actual_temp",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    MtecSensorEntityDescription(
        key="hc1_flow_set_temp",
        mtec_key="hc1_flow_set_temp",
        translation_key="hc1_flow_set_temp",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    MtecSensorEntityDescription(
        key="hc1_return_temp",
        mtec_key="hc1_return_temp",
        translation_key="hc1_return_temp",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    MtecSensorEntityDescription(
        key="hc1_heat_request",
        mtec_key="hc1_heat_request",
        translation_key="hc1_heat_request",
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:fire",
    ),
    MtecSensorEntityDescription(
        key="hc1_cool_request",
        mtec_key="hc1_cool_request",
        translation_key="hc1_cool_request",
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:snowflake",
    ),
    MtecSensorEntityDescription(
        key="hc1_humidity",
        mtec_key="hc1_humidity",
        translation_key="hc1_humidity",
        native_unit_of_measurement=PERCENTAGE,
        device_class=SensorDeviceClass.HUMIDITY,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    MtecSensorEntityDescription(
        key="hc1_mixer",
        mtec_key="hc1_mixer",
        translation_key="hc1_mixer",
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:valve",
    ),
    # Solar
    MtecSensorEntityDescription(
        key="solar_collector_temp",
        mtec_key="solar_collector_temp",
        translation_key="solar_collector_temp",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    # PV
    MtecSensorEntityDescription(
        key="pv_meter_power",
        mtec_key="pv_meter_power",
        translation_key="pv_meter_power",
        native_unit_of_measurement=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    # External heat source
    MtecSensorEntityDescription(
        key="ext_heat_source_request",
        mtec_key="ext_heat_source_request",
        translation_key="ext_heat_source_request",
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:fire-circle",
    ),
    # Alarms
    MtecSensorEntityDescription(
        key="alarm_id_0",
        mtec_key="alarm_id_0",
        translation_key="alarm_id_0",
        icon="mdi:alert-circle",
    ),
    MtecSensorEntityDescription(
        key="alarm_id_1",
        mtec_key="alarm_id_1",
        translation_key="alarm_id_1",
        icon="mdi:alert-circle",
    ),
    MtecSensorEntityDescription(
        key="alarm_id_2",
        mtec_key="alarm_id_2",
        translation_key="alarm_id_2",
        icon="mdi:alert-circle",
    ),
    MtecSensorEntityDescription(
        key="alarm_id_3",
        mtec_key="alarm_id_3",
        translation_key="alarm_id_3",
        icon="mdi:alert-circle",
    ),
    MtecSensorEntityDescription(
        key="alarm_id_4",
        mtec_key="alarm_id_4",
        translation_key="alarm_id_4",
        icon="mdi:alert-circle",
    ),
)


BINARY_SENSOR_DESCRIPTIONS: tuple[MtecBinarySensorEntityDescription, ...] = (
    MtecBinarySensorEntityDescription(
        key="buffer_heat_request",
        mtec_key="buffer_heat_request",
        translation_key="buffer_heat_request",
        icon="mdi:fire",
    ),
    MtecBinarySensorEntityDescription(
        key="buffer_cool_request",
        mtec_key="buffer_cool_request",
        translation_key="buffer_cool_request",
        icon="mdi:snowflake",
    ),
    MtecBinarySensorEntityDescription(
        key="hot_water_heat_request",
        mtec_key="hot_water_heat_request",
        translation_key="hot_water_heat_request",
        icon="mdi:fire",
    ),
    MtecBinarySensorEntityDescription(
        key="hot_water_pump",
        mtec_key="hot_water_pump",
        translation_key="hot_water_pump",
        device_class=BinarySensorDeviceClass.RUNNING,
        icon="mdi:pump",
    ),
    MtecBinarySensorEntityDescription(
        key="hot_water_circ_pump",
        mtec_key="hot_water_circ_pump",
        translation_key="hot_water_circ_pump",
        device_class=BinarySensorDeviceClass.RUNNING,
        icon="mdi:pump",
    ),
    MtecBinarySensorEntityDescription(
        key="hc0_pump",
        mtec_key="hc0_pump",
        translation_key="hc0_pump",
        device_class=BinarySensorDeviceClass.RUNNING,
        icon="mdi:pump",
    ),
    MtecBinarySensorEntityDescription(
        key="hc1_pump",
        mtec_key="hc1_pump",
        translation_key="hc1_pump",
        device_class=BinarySensorDeviceClass.RUNNING,
        icon="mdi:pump",
    ),
    MtecBinarySensorEntityDescription(
        key="pv_excess_energy",
        mtec_key="pv_excess_energy",
        translation_key="pv_excess_energy",
        device_class=BinarySensorDeviceClass.POWER,
        icon="mdi:solar-power",
    ),
    MtecBinarySensorEntityDescription(
        key="ext_heat_source",
        mtec_key="ext_heat_source",
        translation_key="ext_heat_source",
        device_class=BinarySensorDeviceClass.RUNNING,
        icon="mdi:fire-circle",
    ),
    MtecBinarySensorEntityDescription(
        key="screed_drying_active",
        mtec_key="screed_drying_active",
        translation_key="screed_drying_active",
        device_class=BinarySensorDeviceClass.RUNNING,
        icon="mdi:heat-wave",
    ),
)


NUMBER_DESCRIPTIONS: tuple[MtecNumberEntityDescription, ...] = (
    MtecNumberEntityDescription(
        key="hot_water_target_temp",
        mtec_key="hot_water_target_temp",
        translation_key="hot_water_target_temp_set",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=NumberDeviceClass.TEMPERATURE,
        native_min_value=0.0,
        native_max_value=52.0,
        native_step=0.5,
        icon="mdi:water-thermometer",
    ),
    # Heat circuit 0 temperature settings
    MtecNumberEntityDescription(
        key="hc0_day_temp",
        mtec_key="hc0_day_temp",
        translation_key="hc0_day_temp",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=NumberDeviceClass.TEMPERATURE,
        native_min_value=10.0,
        native_max_value=30.0,
        native_step=0.5,
        icon="mdi:weather-sunny",
    ),
    MtecNumberEntityDescription(
        key="hc0_night_temp",
        mtec_key="hc0_night_temp",
        translation_key="hc0_night_temp",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=NumberDeviceClass.TEMPERATURE,
        native_min_value=10.0,
        native_max_value=30.0,
        native_step=0.5,
        icon="mdi:weather-night",
    ),
    MtecNumberEntityDescription(
        key="hc0_offset_temp",
        mtec_key="hc0_offset_temp",
        translation_key="hc0_offset_temp",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=NumberDeviceClass.TEMPERATURE,
        native_min_value=-2.5,
        native_max_value=2.5,
        native_step=0.5,
        icon="mdi:thermometer-plus",
    ),
    # Heat circuit 1 temperature settings
    MtecNumberEntityDescription(
        key="hc1_day_temp",
        mtec_key="hc1_day_temp",
        translation_key="hc1_day_temp",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=NumberDeviceClass.TEMPERATURE,
        native_min_value=10.0,
        native_max_value=30.0,
        native_step=0.5,
        icon="mdi:weather-sunny",
    ),
    MtecNumberEntityDescription(
        key="hc1_night_temp",
        mtec_key="hc1_night_temp",
        translation_key="hc1_night_temp",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=NumberDeviceClass.TEMPERATURE,
        native_min_value=10.0,
        native_max_value=30.0,
        native_step=0.5,
        icon="mdi:weather-night",
    ),
    MtecNumberEntityDescription(
        key="hc1_offset_temp",
        mtec_key="hc1_offset_temp",
        translation_key="hc1_offset_temp",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=NumberDeviceClass.TEMPERATURE,
        native_min_value=-2.5,
        native_max_value=2.5,
        native_step=0.5,
        icon="mdi:thermometer-plus",
    ),
)


SELECT_DESCRIPTIONS: tuple[MtecSelectEntityDescription, ...] = (
    MtecSelectEntityDescription(
        key="system_operating_mode",
        mtec_key="system_operating_mode",
        translation_key="system_operating_mode",
        options_map=SYSTEM_OPERATING_MODE_OPTIONS,
        options=list(SYSTEM_OPERATING_MODE_OPTIONS.values()),
        icon="mdi:cog",
    ),
    MtecSelectEntityDescription(
        key="hot_water_mode",
        mtec_key="hot_water_mode",
        translation_key="hot_water_mode",
        options_map=HOT_WATER_MODE_OPTIONS,
        options=list(HOT_WATER_MODE_OPTIONS.values()),
        icon="mdi:water-boiler",
    ),
    MtecSelectEntityDescription(
        key="hc0_mode",
        mtec_key="hc0_mode",
        translation_key="hc0_mode",
        options_map=HEAT_CIRCUIT_MODE_OPTIONS,
        options=list(HEAT_CIRCUIT_MODE_OPTIONS.values()),
        icon="mdi:radiator",
    ),
    MtecSelectEntityDescription(
        key="hc1_mode",
        mtec_key="hc1_mode",
        translation_key="hc1_mode",
        options_map=HEAT_CIRCUIT_MODE_OPTIONS,
        options=list(HEAT_CIRCUIT_MODE_OPTIONS.values()),
        icon="mdi:radiator",
    ),
    MtecSelectEntityDescription(
        key="sg_ready_mode",
        mtec_key="sg_ready_mode",
        translation_key="sg_ready_mode",
        options_map=SG_READY_MODE_OPTIONS,
        options=list(SG_READY_MODE_OPTIONS.values()),
        icon="mdi:transmission-tower",
    ),
)

PLATFORMS = ["binary_sensor", "climate", "sensor", "number", "select"]
