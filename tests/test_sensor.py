"""Tests for M-TEC sensor platform."""

from __future__ import annotations

from unittest.mock import MagicMock

from custom_components.mtec.sensor import MtecSensor


async def test_sensor_native_value(coordinator_data):
    """Test sensor native value."""
    from custom_components.mtec.const import SENSOR_DESCRIPTIONS

    coordinator = MagicMock()
    coordinator.data = coordinator_data
    coordinator.client.host = "192.168.1.100"

    desc = next(d for d in SENSOR_DESCRIPTIONS if d.key == "outdoor_temp")
    sensor = MtecSensor(coordinator, desc)

    assert sensor.native_value == 15.5


async def test_sensor_native_value_none(coordinator_data):
    """Test sensor when data is None."""
    from custom_components.mtec.const import SENSOR_DESCRIPTIONS

    coordinator = MagicMock()
    coordinator.data = None
    coordinator.client.host = "192.168.1.100"

    desc = next(d for d in SENSOR_DESCRIPTIONS if d.key == "outdoor_temp")
    sensor = MtecSensor(coordinator, desc)

    assert sensor.native_value is None


async def test_sensor_native_value_missing_key(coordinator_data):
    """Test sensor when key is missing from data."""
    from custom_components.mtec.const import SENSOR_DESCRIPTIONS

    coordinator = MagicMock()
    coordinator.data = coordinator_data
    coordinator.client.host = "192.168.1.100"

    desc = next(d for d in SENSOR_DESCRIPTIONS if d.key == "outdoor_temp")
    # Remove the key from data
    del coordinator_data["outdoor_temp"]
    sensor = MtecSensor(coordinator, desc)

    assert sensor.native_value is None


async def test_sensor_enum_mapping(coordinator_data):
    """Test sensor with enum value mapping."""
    from custom_components.mtec.const import SENSOR_DESCRIPTIONS

    coordinator = MagicMock()
    coordinator.data = coordinator_data
    coordinator.client.host = "192.168.1.100"

    desc = next(d for d in SENSOR_DESCRIPTIONS if d.key == "heatpump_state")
    sensor = MtecSensor(coordinator, desc)

    # State 2 should map to "Heating"
    assert sensor.native_value == "Heating"


async def test_sensor_enum_mapping_unknown(coordinator_data):
    """Test sensor with unknown enum value."""
    from custom_components.mtec.const import SENSOR_DESCRIPTIONS

    coordinator = MagicMock()
    coordinator_data["heatpump_state"] = 99  # Unknown state
    coordinator.data = coordinator_data
    coordinator.client.host = "192.168.1.100"

    desc = next(d for d in SENSOR_DESCRIPTIONS if d.key == "heatpump_state")
    sensor = MtecSensor(coordinator, desc)

    assert sensor.native_value == "Unknown (99)"


async def test_sensor_unique_id(coordinator_data):
    """Test sensor unique ID."""
    from custom_components.mtec.const import SENSOR_DESCRIPTIONS

    coordinator = MagicMock()
    coordinator.data = coordinator_data
    coordinator.client.host = "192.168.1.100"

    desc = next(d for d in SENSOR_DESCRIPTIONS if d.key == "outdoor_temp")
    sensor = MtecSensor(coordinator, desc)

    assert sensor.unique_id == "192.168.1.100_outdoor_temp"


async def test_sensor_available(coordinator_data):
    """Test sensor available property."""
    from custom_components.mtec.const import SENSOR_DESCRIPTIONS

    coordinator = MagicMock()
    coordinator.data = coordinator_data
    coordinator.last_update_success = True
    coordinator.client.host = "192.168.1.100"

    desc = next(d for d in SENSOR_DESCRIPTIONS if d.key == "outdoor_temp")
    sensor = MtecSensor(coordinator, desc)

    assert sensor.available is True


async def test_sensor_not_available_when_key_missing(coordinator_data):
    """Test sensor not available when key is missing."""
    from custom_components.mtec.const import SENSOR_DESCRIPTIONS

    coordinator = MagicMock()
    coordinator.data = coordinator_data
    coordinator.last_update_success = True
    coordinator.client.host = "192.168.1.100"

    desc = next(d for d in SENSOR_DESCRIPTIONS if d.key == "outdoor_temp")
    del coordinator_data["outdoor_temp"]
    sensor = MtecSensor(coordinator, desc)

    assert sensor.available is False


async def test_sensor_inherits_sensor_entity():
    """Test that MtecSensor inherits from SensorEntity."""
    from homeassistant.components.sensor import SensorEntity

    assert issubclass(MtecSensor, SensorEntity)


async def test_sensor_device_class_and_unit(coordinator_data):
    """Test sensor device class and unit from description."""
    from homeassistant.components.sensor import SensorDeviceClass, SensorStateClass
    from homeassistant.const import UnitOfTemperature

    from custom_components.mtec.const import SENSOR_DESCRIPTIONS

    coordinator = MagicMock()
    coordinator.data = coordinator_data
    coordinator.client.host = "192.168.1.100"

    desc = next(d for d in SENSOR_DESCRIPTIONS if d.key == "outdoor_temp")
    sensor = MtecSensor(coordinator, desc)

    assert sensor.device_class == SensorDeviceClass.TEMPERATURE
    assert sensor.native_unit_of_measurement == UnitOfTemperature.CELSIUS
    assert sensor.state_class == SensorStateClass.MEASUREMENT
