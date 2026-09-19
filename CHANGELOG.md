# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [v1.2.6] - 2026-09-19

Adds HACS and hassfest validation, reconciles the aiohttp requirement, and guards against version drift between the manifest and pyproject.

### Fixes

- Sort the manifest keys so the integration passes hassfest validation

### CI

- Add hassfest and HACS validation workflows
- Pin the lint tools to the versions under test
- Reconcile the `aiohttp` requirement and drop the unused `dev` extra in favour of `requirements_test.txt`
- Add a test that guards against version drift between the manifest and `pyproject.toml`

### Dependencies

- Bump ruff from 0.16.4 to 0.16.7

### Documentation & Links

- [README](https://github.com/fabianwimberger/homeassistant-mtec-http#readme)

## [v1.2.5] - 2026-08-27

Fixes a heat circuit entity going permanently unavailable after a heat pump restart.

### Fixes

- Fix phantom heat circuit detection incorrectly hiding a real circuit's entities when it's idling in Standby. The probe used to key off `flow_set_temp`, a demand-derived setpoint that reads 0 whenever a circuit has no active heat demand; it now keys off `return_temp`, a physical sensor reading that stays non-zero from residual loop heat regardless of operating mode.

### Dependencies

- Bump `ruff` from 0.16.2 to 0.16.4
- Bump `mypy` from 2.3.0 to 2.3.1
- Align integration version metadata with the release version

### Documentation & Links

- [README](https://github.com/fabianwimberger/homeassistant-mtec-http#readme)

## [v1.2.4] - 2026-08-15

M-TEC Heat Pump now runs against Home Assistant 2026.8.2 and aiohttp 3.14.3, closing out the pending Dependabot security alerts on the aiohttp dependency chain.

### Dependencies

- Bump `homeassistant` test pin from 2026.7.2 to 2026.8.2, unblocking the aiohttp update
- Bump `aiohttp` from 3.14.1 to 3.14.3
- Bump `pytest-homeassistant-custom-component` to 0.13.356 to match
- Bump `ruff` from 0.15.20 to 0.16.2 and `mypy` from 2.1.0 to 2.3.0
- Bump `actions/setup-python` from 6 to 7
- Align integration version metadata with the release version

### Documentation & Links

- [README](https://github.com/fabianwimberger/homeassistant-mtec-http#readme)

## [v1.2.3] - 2026-07-17

M-TEC Heat Pump now runs against Home Assistant 2026.7.2 and aiohttp 3.14.1, closing out the pending Dependabot security alerts on the aiohttp dependency chain.

### Dependencies

- Bump `homeassistant` test pin from 2026.5.1 to 2026.7.2, unblocking the aiohttp update
- Bump `aiohttp` from 3.13.5 to 3.14.1
- Bump `pytest-homeassistant-custom-component` to 0.13.346 and `pytest-aiohttp` to 1.1.1 to match
- Replace unmaintained `aioresponses` with the maintained `aioresponses-ng` fork (same import path), since `aioresponses` is incompatible with aiohttp>=3.14
- Align integration version metadata with the release version

### Documentation & Links

- [README](https://github.com/fabianwimberger/homeassistant-mtec-http#readme)

## [v1.2.2] - 2026-05-10

M-TEC Heat Pump now includes local Home Assistant brand assets so the integration can show an icon in Home Assistant and HACS.

### Changes

- Add Home Assistant brand icon.png and logo.png assets under custom_components/mtec/brand
- Align integration version metadata with the release version

### Documentation & Links

- [README](https://github.com/fabianwimberger/homeassistant-mtec-http#readme)

## [v1.2.1] - 2026-05-09

M-TEC Heat Pump now discovers available signals faster and avoids hiding heating circuits when one probe value is missing.

### Fixes

- Probe M-TEC signals with bounded concurrency during startup
- Keep heating-circuit entities visible when `flow_set_temp` is unavailable instead of treating the circuit as phantom
- Continue filtering phantom heating circuits when `flow_set_temp` is present and zero
- Preserve precision when converting small watt readings to kilowatts
- Align integration version metadata with the release version

### Documentation & Links

- [README](https://github.com/fabianwimberger/homeassistant-mtec-http#readme)

## [v1.2.0] - 2026-05-09

Robustness improvements for MTEC heat pump API client.

### Fixes
- Catch JSON decode errors in API response parsing
- Validate response shape before iteration
- Graceful degradation when individual signals return malformed JSON

### Documentation & Links
- https://github.com/fabianwimberger/homeassistant-mtec-http

## [v1.1.0] - 2026-05-08

Internal refactor extracting hardcoded values to named constants, expanded test coverage, brand-asset cleanup, and routine dependency updates.

### Refactor

- Extracted hardcoded HTTP timeouts, climate temperature limits, and scan interval bounds to named constants
- Use regex for heat circuit key parsing
- Use ``API_ENDPOINT`` constant for base URL construction

### Tests

- Added unit tests for conversion functions
- Added integration tests for entity creation during setup

### Fixes

- Pin test dependencies to exact versions in ``requirements_test.txt``

### Documentation

- Replaced "why this project" section with a Background section
- Added community health files

### Chores

- Added explanations to ``type: ignore`` comments
- Removed third-party brand assets
- Formatted ``test_init.py`` with ruff

### Dependencies

- Bump homeassistant from 2025.1.0 to 2026.2.3
- Bump aiohttp from 3.9.0 to 3.13.5
- Bump aioresponses from 0.7.0 to 0.7.8
- Bump pytest-aiohttp from 1.0.5 to 1.1.0
- Bump pytest-cov from 5.0.0 to 7.1.0
- Bump ruff from 0.8.0 to 0.15.10

### Documentation & Links

- [README](https://github.com/fabianwimberger/homeassistant-mtec-http#readme)

## [v1.0.3] - 2026-04-12

### What's Changed
* Bug fixes: TimeoutError handling, translations, and version bump to 1.0.3 by @fabianwimberger in https://github.com/fabianwimberger/homeassistant-mtec-http/pull/7


**Full Changelog**: https://github.com/fabianwimberger/homeassistant-mtec-http/compare/v1.0.2...v1.0.3

## [v1.0.2] - 2026-04-12

### What's Changed
* Fix race conditions in climate entity by using optimistic updates by @fabianwimberger in https://github.com/fabianwimberger/homeassistant-mtec-http/pull/6
* Improve climate entity availability checks for all required keys
* Improve phantom circuit filtering with debug logging
* Fix write value formatting for whole numbers
* Increase write timeout from 5 to 10 seconds
* Add enum mappings for system_operating_mode, hot_water_mode, sg_ready_mode sensors
* Add codeowner to manifest

**Full Changelog**: https://github.com/fabianwimberger/homeassistant-mtec-http/compare/v1.0.1...v1.0.2

## [v1.0.1] - 2026-04-06

### What's Changed
* Optimistic/Instant state updates for climate entity by @fabianwimberger in https://github.com/fabianwimberger/homeassistant-mtec-http/pull/5


**Full Changelog**: https://github.com/fabianwimberger/homeassistant-mtec-http/compare/v1.0.0...v1.0.1

## [v1.0.0] - 2026-04-05

#### Features
- 70+ entities: sensors, binary sensors, numbers, selects, and climate thermostats
- Climate control with HVAC modes (Off, Auto, Heat) and presets (Day, Night, Vacation, Party)
- Auto-discovery of available signals at startup
- Energy dashboard support (heating and electrical energy sensors)
- Real-time updates with configurable polling interval
- Built-in diagnostics export
- English and German translations

#### Installation
1. Install via HACS as custom repository
2. Restart Home Assistant
3. Add integration via Settings → Devices & Services

#### Notes
- This is a community project, not affiliated with M-TEC
- Requires M-TEC heat pump with HTTP API access (should be default)
