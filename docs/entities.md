# Entities

## Climate (thermostat UI)

| Entity | Description |
|--------|-------------|
| HC0 heating circuit | Heating circuit 0 thermostat (current/target temp, mode) |
| HC1 heating circuit | Heating circuit 1 thermostat (current/target temp, mode) |

HVAC modes: Off, Auto (Timer), Heat (Day). Presets: Day, Night, Vacation, Party.

## Sensors

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

## Binary Sensors

Buffer tank heat/cool request, hot water heat request/pump, HC0/HC1 pump, PV excess energy, external heat source, screed drying.

## Numbers (adjustable)

Hot water target temperature, HC0/HC1 day/night/offset temperatures.

## Selects (mode switches)

System operating mode, hot water mode, HC0/HC1 operating mode, SG Ready mode.
