# M-TEC Heat Pump Integration for Home Assistant

[![CI](https://github.com/fabianwimberger/homeassistant-mtec-http/actions/workflows/ci.yml/badge.svg)](https://github.com/fabianwimberger/homeassistant-mtec-http/actions)
[![codecov](https://codecov.io/gh/fabianwimberger/homeassistant-mtec-http/branch/main/graph/badge.svg)](https://codecov.io/gh/fabianwimberger/homeassistant-mtec-http)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

> **⚠️ Disclaimer**: This is an independent, open-source project created by the community. It is **not affiliated with, endorsed by, or sponsored by M-TEC or mtec-systems**. "M-TEC" and the M-TEC logo are trademarks of their respective owners. Use at your own risk.

Custom integration for [Home Assistant](https://www.home-assistant.io/) that communicates directly with M-TEC heat pumps via their built-in HTTP API (`/var/readWriteVars`). No MQTT broker or middleman needed.

## Background

M-TEC heat pumps expose a local HTTP API, but there is no native Home Assistant integration for it. Existing options rely on MQTT bridges or extra hardware. This talks to the pump directly, auto-discovers which signals the unit supports, and exposes them as HA entities including climate controls and energy-dashboard sensors.

## Features

- **70+ entities** — sensors, binary sensors, numbers, selects, and climate thermostats
- **Auto-discovery** — probes available signals at startup (units vary by configuration)
- **Climate control** — thermostat UI for heating circuits with HVAC modes and presets
- **Energy dashboard** — total heating and electrical energy sensors with `total_increasing` state class; add them under **Settings > Dashboards > Energy**
- **Real-time updates** — configurable polling interval (5-300 seconds)
- **Diagnostics** — **Download diagnostics** on the integration page dumps the configuration, probed signals, and current values
- **Multi-language** — English and German translations included

## Quick Start

### Installation (HACS - Recommended)

1. Open HACS in Home Assistant
2. Click the three dots in the top right and select **Custom repositories**
3. Add `https://github.com/fabianwimberger/homeassistant-mtec-http` as an **Integration**
4. Search for "M-TEC Heat Pump" and install it
5. Restart Home Assistant

### Installation (Manual)

```bash
# Clone into your Home Assistant custom_components directory
cd /path/to/homeassistant/config
git clone https://github.com/fabianwimberger/homeassistant-mtec-http.git
mv homeassistant-mtec-http/custom_components/mtec custom_components/
rm -rf homeassistant-mtec-http
```

Restart Home Assistant.

### Configuration

1. Go to **Settings > Devices & Services > Add Integration**
2. Search for "M-TEC Heat Pump"
3. Enter the IP address of your heat pump (default: `192.168.1.100`)
4. Set the scan interval in seconds (default: 15, range: 5-300)

The integration validates the connection by reading the outdoor temperature before completing setup.

## How It Works

```
Startup → Probe available signals → Read device info → Create entities → Poll for updates
```

The M-TEC API returns HTTP 500 if any requested signal doesn't exist on the unit. At startup, the integration probes each signal individually to determine which entities to create. This handles different heat pump configurations without manual setup.

- Communicates via HTTP POST to `http://<host>/var/readWriteVars`
- All entities share a single HA device ("M-TEC Heat Pump") that shows firmware version and serial number
- The API covers up to 8 heating circuits, 4 hot water tanks, and 4 heat pumps; HC0/HC1 and heatpump[0] are implemented

## Entities

Two climate entities (HC0/HC1 thermostats with Off, Auto and Heat modes and Day, Night, Vacation and Party presets), sensors for temperatures, pressures, power and energy, plus binary sensors, numbers and selects for the adjustable values. Only signals the unit reports are created. The list is in [docs/entities.md](docs/entities.md).

## Configuration

### Changing Settings After Setup

- **Host**: Use the "Reconfigure" option on the integration card to change the IP address
- **Scan interval**: Use the "Configure" option to adjust the polling interval at runtime

## Troubleshooting

If entities are missing or unavailable, check that the heat pump's web interface is reachable from Home Assistant, then download diagnostics to see which signals were probed. Signals the unit does not support are not created.

## License

MIT License — see [LICENSE](LICENSE) file.
