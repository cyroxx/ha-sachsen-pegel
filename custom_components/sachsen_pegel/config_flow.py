from __future__ import annotations

from typing import Any

import aiohttp
import voluptuous as vol

from homeassistant.config_entries import ConfigFlow, ConfigFlowResult
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.selector import (
    SelectOptionDict,
    SelectSelector,
    SelectSelectorConfig,
    SelectSelectorMode,
)

from .const import (
    CONF_BASE_URL,
    CONF_STATION_ID,
    DEFAULT_BASE_URL,
    DOMAIN,
    REQUEST_TIMEOUT,
)


class SachsenPegelConfigFlow(ConfigFlow, domain=DOMAIN):
    VERSION = 1

    def __init__(self) -> None:
        self._base_url = DEFAULT_BASE_URL
        self._stations: dict[str, str] = {}

    async def _fetch_stations(self, base_url: str) -> dict[str, str]:
        session = async_get_clientsession(self.hass)
        async with session.get(
            f"{base_url}/api/pegel",
            timeout=aiohttp.ClientTimeout(total=REQUEST_TIMEOUT),
        ) as resp:
            resp.raise_for_status()
            data = await resp.json()
        return {
            item["station_id"]: item.get("station_title") or item["station_id"]
            for item in data["items"]
        }

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        errors: dict[str, str] = {}
        if user_input is not None:
            base_url = user_input[CONF_BASE_URL].rstrip("/")
            try:
                stations = await self._fetch_stations(base_url)
            except (aiohttp.ClientError, TimeoutError, KeyError, TypeError, ValueError):
                errors["base"] = "cannot_connect"
            else:
                if not stations:
                    errors["base"] = "no_stations"
                else:
                    self._base_url = base_url
                    self._stations = stations
                    return await self.async_step_station()

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {vol.Required(CONF_BASE_URL, default=self._base_url): str}
            ),
            errors=errors,
        )

    async def async_step_station(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        if user_input is not None:
            station_id = user_input[CONF_STATION_ID]
            await self.async_set_unique_id(station_id)
            self._abort_if_unique_id_configured()
            return self.async_create_entry(
                title=self._stations[station_id],
                data={CONF_BASE_URL: self._base_url, CONF_STATION_ID: station_id},
            )

        options = [
            SelectOptionDict(value=sid, label=f"{title} ({sid})")
            for sid, title in sorted(self._stations.items(), key=lambda kv: kv[1])
        ]
        return self.async_show_form(
            step_id="station",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_STATION_ID): SelectSelector(
                        SelectSelectorConfig(
                            options=options, mode=SelectSelectorMode.DROPDOWN
                        )
                    )
                }
            ),
        )
