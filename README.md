# M-TEC Heat Pump Integration for Home Assistant

[![CI](https://github.com/fabianwimberger/homeassistant-mtec-http/actions/workflows/ci.yml/badge.svg)](https://github.com/fabianwimberger/homeassistant-mtec-http/actions)
[![codecov](https://codecov.io/gh/fabianwimberger/homeassistant-mtec-http/branch/main/graph/badge.svg)](https://codecov.io/gh/fabianwimberger/homeassistant-mtec-http)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

> **⚠️ Disclaimer**: This is an independent, open-source project created by the community. It is **not affiliated with, endorsed by, or sponsored by M-TEC or mtec-systems**. "M-TEC" and the M-TEC logo are trademarks of their respective owners. Use at your own risk.

Custom integration for [Home Assistant](https://www.home-assistant.io/) that communicates directly with M-TEC heat pumps via their built-in HTTP API (`/var/readWriteVars`). No MQTT broker or middleman needed.

## Why This Project?

M-TEC heat pumps expose a rich set of operational data and controls via their local HTTP API, but there's no native Home Assistant integration. Existing solutions require additional hardware, MQTT brokers, or custom scripting. This integration provides a plug-and-play solution that auto-discovers available sensors based on your specific heat pump configuration.

**Goals:**
- Provide native Home Assistant integration for M-TEC heat pumps
- Auto-discover available sensors (different units have different capabilities)
- Support both monitoring and control (climate, setpoints, operating modes)
- Integrate with HA Energy Dashboard for consumption tracking

## Features

- **70+ entities** — sensors, binary sensors, numbers, selects, and climate thermostats
- **Auto-discovery** — probes available signals at startup (units vary by configuration)
- **Climate control** — thermostat UI for heating circuits with HVAC modes and presets
- **Energy dashboard** — heating and electrical energy sensors with `total_increasing` state class
- **Real-time updates** — configurable polling interval (5-300 seconds)
- **Diagnostics** — built-in HA diagnostics export for troubleshooting
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

The M-TEC API returns HTTP 500 if any requested signal doesn't exist on the unit. At startup, the integration probes each signal individually to determine which entities to create. This handles different heat pump configurations without manual configuration.

## Entities

### Climate (thermostat UI)

| Entity | Description |
|--------|-------------|
| HC0 heating circuit | Heating circuit 0 thermostat (current/target temp, mode) |
| HC1 heating circuit | Heating circuit 1 thermostat (current/target temp, mode) |

HVAC modes: Off, Auto (Timer), Heat (Day). Presets: Day, Night, Vacation, Party.

### Sensors

| Entity | Unit | Description |
|--------|------|-------------|
| Outdoor temperature | °C | Outside air temperature |
| Heating power | kW | Current heating output |
| Electrical power | W | Current electrical consumption |
| Heat pump state | — | Standby/Pre-Run/Heating/Defrost/Cooling/Post-Run/Safety Shutdown/Error |
| COP | — | Coefficient of performance |
| Total heating energy | kWh | Accumulated heating energy (energy dashboard) |
| Total electrical energy | kWh | Accumulated electrical energy (energy dashboard) |
| Operating hours | h | Total compressor hours |
| Vaporizer / condenser temp | °C | Refrigerant circuit temperatures |
| Heat flow / return temp | °C | Supply and return temperatures |
| Source in / out temp | °C | Source (ground/air) temperatures |
| Compressor in / out temp | °C | Compressor suction/discharge |
| Low / high pressure | bar | Refrigerant pressures |
| Superheat actual / setpoint | °C | Superheat control |
| Circulation pump / compressor / fan | % | Actuator speeds |
| Mass flow | kg/h | Refrigerant mass flow rate |
| Buffer tank top / mid / set temp | °C | Buffer tank sensors |
| Hot water top / circ temp | °C | Hot water tank sensors |
| HC0/HC1 room temp / set temp | °C | Room temperatures per circuit |
| Solar collector temp | °C | Solar thermal collector |
| PV meter power | W | PV excess energy from meter |
| Alarm 1-5 | — | Pending alarm IDs (0 = no alarm) |

See the full entity list in the [documentation](https://github.com/fabianwimberger/homeassistant-mtec-http).

### Binary Sensors

Buffer tank heat/cool request, hot water heat request/pump, HC0/HC1 pump, PV excess energy, external heat source, screed drying.

### Numbers (adjustable)

Hot water target temperature, HC0/HC1 day/night/offset temperatures.

### Selects (mode switches)

System operating mode, hot water mode, HC0/HC1 operating mode, SG Ready mode.

## Energy Dashboard

The **Total heating energy** and **Total electrical energy** sensors are compatible with the Home Assistant energy dashboard. Add them under **Settings > Dashboards > Energy**.

## Diagnostics

The integration supports Home Assistant's built-in diagnostics export. Go to the integration page and click **Download diagnostics** to get a JSON dump of the current configuration and sensor values.

## Configuration

### Changing Settings After Setup

- **Host**: Use the "Reconfigure" option on the integration card to change the IP address
- **Scan interval**: Use the "Configure" option to adjust the polling interval at runtime

## Device Info

The device card shows:
- Manufacturer: M-TEC
- Firmware version (read from the heat pump)
- Serial number (read from the heat pump)

## Technical Details

- Communicates via HTTP POST to `http://<host>/var/readWriteVars`
- All entities share a single HA device ("M-TEC Heat Pump")
- Entities report as unavailable when the heat pump is unreachable
- Supports up to 8 heating circuits, 4 hot water tanks, and 4 heat pumps in the Modbus spec (currently HC0/HC1 and heatpump[0] are implemented)

## Troubleshooting

**No entities appearing:**
- Verify the heat pump IP address is correct
- Check that the heat pump web interface is accessible
- Download diagnostics to see which signals were probed

**Entities showing as unavailable:**
- Check network connectivity to the heat pump
- Some entities may not be available on your specific unit configuration

## License & Disclaimer

MIT License — see [LICENSE](LICENSE) file.

### Third-Party Trademarks

This project uses the "M-TEC" name and logo to identify the compatible heat pump systems. "M-TEC" is a trademark of M-TEC or mtec-systems. This project is an independent, community-created integration and is **not affiliated with, endorsed by, or sponsored by M-TEC or mtec-systems**. Use of the M-TEC trademark is for identification and compatibility purposes only.
