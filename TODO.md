# M-TEC Heat Pump HA Integration

## Current State
Integration is feature-complete with 70+ entities verified against a real M-TEC heat pump
(firmware 1.33.7.0). All enums match the official Modbus documentation. Signal probing at
startup handles different M-TEC configurations. Energy sensors support the HA energy dashboard.

## Completed
- [x] GitHub Actions CI workflow (lint with ruff, type check with mypy, test with pytest)
- [x] Unit tests with pytest and aiohttp mocking (~85 tests)
- [x] Logo/icon for the integration (custom SVG)
- [x] Dependencies updated for Home Assistant 2025.x (Python 3.13, aiohttp 3.9+)

## Remaining
- [ ] Test config flow UI and write round-trip in a running Home Assistant instance
- [ ] Support multiple heat pumps (heatpump[1], etc.) and heat circuits [2]-[7]
