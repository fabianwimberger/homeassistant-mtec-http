"""Tests for M-TEC base entity."""

from __future__ import annotations

from unittest.mock import MagicMock

from custom_components.mtec.const import DOMAIN
from custom_components.mtec.entity import MtecEntity


def test_entity_device_info(coordinator_data):
    """Test entity device info."""
    coordinator = MagicMock()
    coordinator.data = coordinator_data
    coordinator.last_update_success = True
    coordinator.client.host = "192.168.1.100"
    coordinator.device_info_data = {
        "firmware_version": "1.33.7.0",
        "serial_number": "WP123456",
    }

    entity = MtecEntity(coordinator)

    assert entity.device_info is not None
    assert entity.device_info["identifiers"] == {(DOMAIN, "192.168.1.100")}
    assert entity.device_info["name"] == "M-TEC Heat Pump"
    assert entity.device_info["manufacturer"] == "M-TEC"
    assert entity.device_info["model"] == "Heat Pump"
    assert entity.device_info["sw_version"] == "1.33.7.0"
    assert entity.device_info["serial_number"] == "WP123456"


def test_entity_device_info_minimal():
    """Test entity device info with minimal data."""
    coordinator = MagicMock()
    coordinator.data = {}
    coordinator.last_update_success = True
    coordinator.client.host = "192.168.1.100"
    coordinator.device_info_data = {}

    entity = MtecEntity(coordinator)

    assert entity.device_info is not None
    assert entity.device_info["sw_version"] is None
    assert entity.device_info["serial_number"] is None


def test_entity_available(coordinator_data):
    """Test entity available when data is present."""
    coordinator = MagicMock()
    coordinator.data = coordinator_data
    coordinator.last_update_success = True
    coordinator.client.host = "192.168.1.100"
    coordinator.device_info_data = {}

    entity = MtecEntity(coordinator)
    entity._mtec_key = "outdoor_temp"

    assert entity.available is True


def test_entity_not_available_when_no_data(coordinator_data):
    """Test entity not available when coordinator has no data."""
    coordinator = MagicMock()
    coordinator.data = None
    coordinator.last_update_success = True
    coordinator.client.host = "192.168.1.100"
    coordinator.device_info_data = {}

    entity = MtecEntity(coordinator)
    entity._mtec_key = "outdoor_temp"

    assert entity.available is False


def test_entity_not_available_when_key_missing(coordinator_data):
    """Test entity not available when key is missing."""
    coordinator = MagicMock()
    coordinator.data = coordinator_data
    coordinator.last_update_success = True
    coordinator.client.host = "192.168.1.100"
    coordinator.device_info_data = {}

    entity = MtecEntity(coordinator)
    entity._mtec_key = "missing_key"

    assert entity.available is False


def test_entity_not_available_when_update_failed(coordinator_data):
    """Test entity not available when last update failed."""
    coordinator = MagicMock()
    coordinator.data = coordinator_data
    coordinator.last_update_success = False
    coordinator.client.host = "192.168.1.100"
    coordinator.device_info_data = {}

    entity = MtecEntity(coordinator)
    entity._mtec_key = "outdoor_temp"

    assert entity.available is False


def test_entity_has_entity_name():
    """Test entity has entity name flag."""
    coordinator = MagicMock()
    coordinator.data = {}
    coordinator.last_update_success = True
    coordinator.client.host = "192.168.1.100"
    coordinator.device_info_data = {}

    entity = MtecEntity(coordinator)

    assert entity._attr_has_entity_name is True
