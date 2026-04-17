"""Tests for M-TEC conversion functions."""

from __future__ import annotations

import pytest

from custom_components.mtec.const import (
    conv_bar,
    conv_energy,
    conv_hours,
    conv_int,
    conv_mass_flow,
    conv_percent,
    conv_temp1,
    conv_temp2,
    conv_watts_kw,
)


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        (21.456, 21.5),
        (21.449, 21.4),
        (0.0, 0.0),
        (-5.678, -5.7),
    ],
)
def test_conv_temp1(value: float, expected: float) -> None:
    assert conv_temp1(value) == expected


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        (21.4567, 21.46),
        (21.4444, 21.44),
        (0.0, 0.0),
        (-5.6789, -5.68),
    ],
)
def test_conv_temp2(value: float, expected: float) -> None:
    assert conv_temp2(value) == expected


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        (3.9, 3),
        (0.0, 0),
        (-2.7, -2),
    ],
)
def test_conv_int(value: float, expected: int) -> None:
    assert conv_int(value) == expected


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        (3600.0, 1.0),
        (7200.0, 2.0),
        (5400.0, 1.5),
        (0.0, 0.0),
    ],
)
def test_conv_hours(value: float, expected: float) -> None:
    assert conv_hours(value) == expected


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        (0.5, 50.0),
        (1.0, 100.0),
        (0.0, 0.0),
        (0.333, 33.3),
    ],
)
def test_conv_percent(value: float, expected: float) -> None:
    assert conv_percent(value) == expected


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        (1.0, 3600),
        (0.5, 1800),
        (0.0, 0),
    ],
)
def test_conv_mass_flow(value: float, expected: float) -> None:
    assert conv_mass_flow(value) == expected


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        (1000.0, 1.0),
        (1500.0, 1.5),
        (0.0, 0.0),
        (999.4, 0.999),
    ],
)
def test_conv_watts_kw(value: float, expected: float) -> None:
    assert conv_watts_kw(value) == expected


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        (1.234, 1.23),
        (0.0, 0.0),
        (3.456, 3.46),
    ],
)
def test_conv_bar(value: float, expected: float) -> None:
    assert conv_bar(value) == expected


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        (12.34, 12.3),
        (0.0, 0.0),
        (99.95, 100.0),
    ],
)
def test_conv_energy(value: float, expected: float) -> None:
    assert conv_energy(value) == expected
