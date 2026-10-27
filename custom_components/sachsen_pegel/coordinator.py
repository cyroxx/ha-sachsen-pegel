from __future__ import annotations

import logging
from typing import Any

import aiohttp

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import CONF_BASE_URL, CONF_STATION_ID, DOMAIN, REQUEST_TIMEOUT, SCAN_INTERVAL

_LOGGER = logging.getLogger(__name__)


class PegelCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Fetches the readings of a gauge station from the proxy."""

    config_entry: ConfigEntry

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        super().__init__(
            hass,
            _LOGGER,
            config_entry=entry,
            name=f"{DOMAIN}_{entry.data[CONF_STATION_ID]}",
            update_interval=SCAN_INTERVAL,
        )
        self.station_id: str = entry.data[CONF_STATION_ID]
        self._url = f"{entry.data[CONF_BASE_URL]}/api/pegel/{self.station_id}"
        self._session = async_get_clientsession(hass)

    async def _async_update_data(self) -> dict[str, Any]:
        try:
            async with self._session.get(
                self._url, timeout=aiohttp.ClientTimeout(total=REQUEST_TIMEOUT)
            ) as resp:
                resp.raise_for_status()
                payload = await resp.json()
        except (aiohttp.ClientError, TimeoutError) as err:
            raise UpdateFailed(f"Fetching {self._url} failed: {err}") from err

        latest = payload.get("latest")
        if not isinstance(latest, dict):
            raise UpdateFailed("Response contains no reading (latest)")
        return {"station_title": payload.get("station_title"), **latest}
