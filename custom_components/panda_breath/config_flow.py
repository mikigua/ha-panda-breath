"""Config flow for Panda Breath integration."""
from __future__ import annotations

import asyncio
import logging
from typing import Any

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.components import zeroconf
from homeassistant.data_entry_flow import FlowResult

from .const import DOMAIN, MDNS_HOSTNAMES, DEFAULT_PORT
from .websocket_client import PandaBreathClient

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required("host", default="pandabreath.local"): str,
        vol.Optional("port", default=DEFAULT_PORT): int,
    }
)


async def _try_connect(host: str, port: int) -> bool:
    """Try to connect to the Panda Breath device."""
    client = PandaBreathClient(host, port)
    return await client.test_connection()


async def _discover_device() -> tuple[str, int] | None:
    """
    Try to auto-discover the Panda Breath by trying known mDNS hostnames.
    Returns (host, port) if found, None otherwise.
    """
    for hostname in MDNS_HOSTNAMES:
        _LOGGER.debug("Trying discovery with hostname: %s", hostname)
        try:
            client = PandaBreathClient(hostname, DEFAULT_PORT)
            if await client.test_connection():
                _LOGGER.info("Panda Breath found at %s", hostname)
                return hostname, DEFAULT_PORT
        except Exception:
            continue
    return None


class PandaBreathConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle the config flow for Panda Breath."""

    VERSION = 1

    def __init__(self) -> None:
        self._discovered_host: str | None = None
        self._discovered_port: int = DEFAULT_PORT

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle manual configuration by the user."""
        errors: dict[str, str] = {}

        if user_input is not None:
            host = user_input["host"]
            port = user_input.get("port", DEFAULT_PORT)

            await self.async_set_unique_id(host)
            self._abort_if_unique_id_configured()

            if await _try_connect(host, port):
                return self.async_create_entry(
                    title=f"Panda Breath ({host})",
                    data={"host": host, "port": port},
                )
            else:
                errors["base"] = "cannot_connect"

        return self.async_show_form(
            step_id="user",
            data_schema=STEP_USER_DATA_SCHEMA,
            errors=errors,
        )

    async def async_step_zeroconf(
        self, discovery_info: zeroconf.ZeroconfServiceInfo
    ) -> FlowResult:
        """Handle auto-discovery via mDNS/Zeroconf."""
        host = discovery_info.host
        port = discovery_info.port or DEFAULT_PORT

        await self.async_set_unique_id(host)
        self._abort_if_unique_id_configured()

        self._discovered_host = host
        self._discovered_port = port

        self.context["title_placeholders"] = {"host": host}
        return await self.async_step_discovery_confirm()

    async def async_step_discovery_confirm(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Ask the user to confirm the discovered device."""
        if user_input is not None:
            return self.async_create_entry(
                title=f"Panda Breath ({self._discovered_host})",
                data={
                    "host": self._discovered_host,
                    "port": self._discovered_port,
                },
            )

        return self.async_show_form(
            step_id="discovery_confirm",
            description_placeholders={"host": self._discovered_host},
        )

    async def async_step_import(self, import_data: dict[str, Any]) -> FlowResult:
        """Handle import from configuration.yaml (legacy support)."""
        return await self.async_step_user(import_data)
