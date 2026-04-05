"""Tests for M-TEC binary sensor platform."""

from __future__ import annotations

from typing import Any
from unittest.mock import MagicMock

from custom_components.mtec.binary_sensor import MtecBinarySensor
from custom_components.mtec.const import BINARY_SENSOR_DESCRIPTIONS


def test_binary_sensor_is_on_true(coordinator_data: dict[str, Any]) -> None:
    """Test binary sensor is on when value is True/1."""
    coordinator = MagicMock()
    coordinator.data = coordinator_data
    coordinator.last_update_success = True
    coordinator.client.host = "192.168.1.100"

    desc = next(d for d in BINARY_SENSOR_DESCRIPTIONS if d.key == "buffer_heat_request")
    sensor = MtecBinarySensor(coordinator, desc)

    assert sensor.is_on is True


def test_binary_sensor_is_on_false(coordinator_data: dict[str, Any]) -> None:
    """Test binary sensor is off when value is False/0."""
    coordinator = MagicMock()
    coordinator_data["hot_water_heat_request"] = 0
    coordinator.data = coordinator_data
    coordinator.last_update_success = True
    coordinator.client.host = "192.168.1.100"

    desc = next(d for d in BINARY_SENSOR_DESCRIPTIONS if d.key == "hot_water_heat_request")
    sensor = MtecBinarySensor(coordinator, desc)

    assert sensor.is_on is False


def test_binary_sensor_is_on_none(coordinator_data: dict[str, Any]) -> None:
    """Test binary sensor returns None when data is None."""
    coordinator = MagicMock()
    coordinator.data = None
    coordinator.last_update_success = True
    coordinator.client.host = "192.168.1.100"

    desc = next(d for d in BINARY_SENSOR_DESCRIPTIONS if d.key == "buffer_heat_request")
    sensor = MtecBinarySensor(coordinator, desc)

    assert sensor.is_on is None


def test_binary_sensor_unique_id(coordinator_data: dict[str, Any]) -> None:
    """Test binary sensor unique ID."""
    coordinator = MagicMock()
    coordinator.data = coordinator_data
    coordinator.last_update_success = True
    coordinator.client.host = "192.168.1.100"

    desc = next(d for d in BINARY_SENSOR_DESCRIPTIONS if d.key == "buffer_heat_request")
    sensor = MtecBinarySensor(coordinator, desc)

    assert sensor.unique_id == "192.168.1.100_buffer_heat_request_binary"


def test_binary_sensor_device_class(coordinator_data: dict[str, Any]) -> None:
    """Test binary sensor device class."""
    coordinator = MagicMock()
    coordinator.data = coordinator_data
    coordinator.last_update_success = True
    coordinator.client.host = "192.168.1.100"

    desc = next(d for d in BINARY_SENSOR_DESCRIPTIONS if d.key == "hc0_pump")
    sensor = MtecBinarySensor(coordinator, desc)

    assert sensor.device_class is not None
