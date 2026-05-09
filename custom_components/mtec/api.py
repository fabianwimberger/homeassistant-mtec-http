"""M-TEC Heat Pump HTTP API client."""

from __future__ import annotations

import asyncio
import contextlib
import json
import logging
import re

import aiohttp

from .const import (
    API_ENDPOINT,
    CONVERSIONS,
    SIGNAL_MAP,
    SIGNAL_MAP_REV,
    TIMEOUT_DEFAULT,
    TIMEOUT_READ,
)

_LOGGER = logging.getLogger(__name__)

PROBE_CONCURRENCY = 16
_HC_KEY_RE = re.compile(r"^(hc\d+)_")


class MtecApiError(Exception):
    """Error communicating with M-TEC heat pump."""


class MtecApiClient:
    """Client for the M-TEC heat pump HTTP API."""

    def __init__(self, host: str, session: aiohttp.ClientSession) -> None:
        self._host = host
        self._session = session
        self._base_url = f"http://{host}{API_ENDPOINT}"
        self._available_keys: set[str] | None = None

    @property
    def host(self) -> str:
        return self._host

    @property
    def available_keys(self) -> set[str]:
        """Return the set of signal keys available on this unit."""
        return self._available_keys or set()

    async def async_validate_connection(self) -> bool:
        """Validate we can connect to the heat pump."""
        try:
            data = await self._async_read_raw(["outdoor_temp"])
            return "outdoor_temp" in data
        except MtecApiError:
            return False

    async def async_read_device_info(self, signals: dict[str, str]) -> dict[str, str]:
        """Read device info signals (version, serial, etc.).

        These are read once at setup. Signals that fail are silently skipped.
        """
        result: dict[str, str] = {}
        for key, signal_name in signals.items():
            try:
                async with self._session.post(
                    self._base_url,
                    json=[{"name": signal_name}],
                    timeout=aiohttp.ClientTimeout(total=TIMEOUT_DEFAULT),
                ) as resp:
                    if resp.status != 200:
                        continue
                    data = await resp.json()
                    if data and isinstance(data, list) and "value" in data[0]:
                        result[key] = str(data[0]["value"])
            except (aiohttp.ClientError, TimeoutError, json.JSONDecodeError):
                continue
        return result

    async def async_probe_available_keys(self) -> set[str]:
        """Probe which signal keys are available on this heat pump.

        The M-TEC API returns HTTP 500 if any requested signal doesn't exist,
        so we must probe individually for signals that may not be present.

        Additionally, heating circuits that return flow_set_temp == 0 are
        considered phantom circuits and are filtered out.
        """
        if self._available_keys is not None:
            return self._available_keys

        semaphore = asyncio.Semaphore(PROBE_CONCURRENCY)

        async def probe_signal(key: str, signal_name: str) -> tuple[str, float] | None:
            async with semaphore:
                value: float | None = None
                matched = False
                request_body = [{"name": signal_name}]
                timeout = aiohttp.ClientTimeout(total=TIMEOUT_DEFAULT)
                try:
                    async with self._session.post(
                        self._base_url,
                        json=request_body,
                        timeout=timeout,
                    ) as resp:
                        if resp.status == 200:
                            data = await resp.json()
                            if data and isinstance(data, list) and "value" in data[0]:
                                matched = True
                                with contextlib.suppress(ValueError, TypeError):
                                    value = float(data[0]["value"])
                except (aiohttp.ClientError, TimeoutError, json.JSONDecodeError):
                    return None
                if matched:
                    return key, value if value is not None else 0.0
                return None

        probe_results = await asyncio.gather(
            *(probe_signal(key, signal_name) for key, signal_name in SIGNAL_MAP.items())
        )

        available: set[str] = set()
        hc_flow_set_temps: dict[str, float] = {}
        for result in probe_results:
            if result is None:
                continue
            key, value = result
            available.add(key)
            if key.endswith("_flow_set_temp"):
                hc_flow_set_temps[key] = value

        filtered_circuits: set[str] = set()
        unfiltered_circuits: set[str] = set()
        for key in list(available):
            match = _HC_KEY_RE.match(key)
            if match:
                hc_num = match.group(1)
                flow_set_key = f"{hc_num}_flow_set_temp"
                if flow_set_key in hc_flow_set_temps and hc_flow_set_temps[flow_set_key] == 0:
                    available.discard(key)
                    filtered_circuits.add(hc_num)
                else:
                    unfiltered_circuits.add(hc_num)

        self._available_keys = available
        _LOGGER.debug("Probed %d/%d available signals", len(available), len(SIGNAL_MAP))
        _LOGGER.debug("Filtered phantom circuits: %s", sorted(filtered_circuits))
        _LOGGER.debug("Active circuits: %s", sorted(unfiltered_circuits))
        return available

    async def async_read_values(self, keys: list[str] | None = None) -> dict[str, float | int]:
        """Read values from the heat pump.

        Only requests signals known to be available on this unit.
        """
        if self._available_keys is None:
            await self.async_probe_available_keys()

        if keys is None:
            keys = list(self._available_keys or SIGNAL_MAP.keys())
        else:
            if self._available_keys is not None:
                keys = [k for k in keys if k in self._available_keys]

        return await self._async_read_raw(keys)

    async def _async_read_raw(self, keys: list[str]) -> dict[str, float | int]:
        """Read values from the heat pump without availability filtering."""
        request_body = [{"name": SIGNAL_MAP[k]} for k in keys if k in SIGNAL_MAP]

        try:
            async with self._session.post(
                self._base_url,
                json=request_body,
                timeout=aiohttp.ClientTimeout(total=TIMEOUT_READ),
            ) as resp:
                if resp.status != 200:
                    raise MtecApiError(f"HTTP {resp.status}")
                response_data = await resp.json()
        except aiohttp.ClientError as err:
            raise MtecApiError(f"Connection error: {err}") from err
        except TimeoutError as err:
            raise MtecApiError(f"Timeout connecting to {self._host}") from err
        except json.JSONDecodeError as err:
            raise MtecApiError(f"Invalid JSON: {err}") from err

        if not isinstance(response_data, list):
            raise MtecApiError(
                f"Unexpected response format: expected list, got {type(response_data).__name__}"
            )

        result: dict[str, float | int] = {}
        for item in response_data:
            name = item.get("name")
            value = item.get("value")
            if name is None or value is None:
                _LOGGER.debug("Skipping item with missing fields: %s", item)
                continue

            key = SIGNAL_MAP_REV.get(name)
            if key is None:
                continue

            float_val = _parse_value(value)
            if float_val is None:
                _LOGGER.warning("Could not parse value %r for %s", value, name)
                continue

            conv = CONVERSIONS.get(key)
            result[key] = conv(float_val) if conv else float_val

        return result

    async def async_write_value(self, key: str, value: float) -> None:
        """Write a value to the heat pump."""
        signal_name = SIGNAL_MAP.get(key)
        if signal_name is None:
            raise MtecApiError(f"Unknown signal key: {key}")

        conv = CONVERSIONS.get(key)
        value_str = str(int(value)) if conv and value == int(value) else str(value)

        request_body = [{"name": signal_name, "value": value_str}]

        try:
            async with self._session.post(
                f"{self._base_url}?action=set",
                json=request_body,
                timeout=aiohttp.ClientTimeout(total=TIMEOUT_DEFAULT),
            ) as resp:
                if resp.status != 200:
                    raise MtecApiError(f"HTTP {resp.status} writing {key}")
        except (aiohttp.ClientError, TimeoutError) as err:
            raise MtecApiError(f"Connection error writing {key}: {err}") from err

        _LOGGER.debug("SET %s=%s", key, value_str)


def _parse_value(value: object) -> float | None:
    """Parse a value from the API response to a float."""
    if isinstance(value, bool):
        return 1.0 if value else 0.0
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        if value == "true":
            return 1.0
        if value == "false":
            return 0.0
        try:
            return float(value)
        except ValueError:
            return None
    return None
