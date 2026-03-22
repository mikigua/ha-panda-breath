"""Panda Breath integration for Home Assistant."""
from __future__ import annotations

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady

from .const import DOMAIN
from .coordinator import PandaBreathCoordinator
from .websocket_client import PandaBreathClient

_LOGGER = logging.getLogger(__name__)

PLATFORMS = ["switch", "select", "number", "sensor"]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Panda Breath from a config entry."""
    host = entry.data["host"]
    port = entry.data.get("port", 80)

    client = PandaBreathClient(host, port)

    # Test connection before setting up
    if not await client.test_connection():
        raise ConfigEntryNotReady(f"Cannot connect to Panda Breath at {host}:{port}")

    coordinator = PandaBreathCoordinator(hass, client)

    # First data fetch
    await coordinator.async_config_entry_first_refresh()

    # Start real-time listener for warehouse_temper
    await coordinator.start_listener()

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    # Handle entry unload
    entry.async_on_unload(entry.add_update_listener(_async_update_listener))

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    coordinator: PandaBreathCoordinator = hass.data[DOMAIN][entry.entry_id]
    await coordinator.stop_listener()

    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok


async def _async_update_listener(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Handle options update."""
    await hass.config_entries.async_reload(entry.entry_id)
