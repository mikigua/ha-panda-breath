"""Coordinator for Panda Breath integration."""
from __future__ import annotations

import asyncio
import logging
from datetime import timedelta
from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import (
    DOMAIN,
    UPDATE_INTERVAL,
    KEY_WORK_ON,
    KEY_WORK_MODE,
    KEY_SET_TEMP,
    KEY_FILTER_TEMP,
    KEY_HOTBED_TEMP,
    KEY_WAREHOUSE_TEMPER,
    KEY_FW_VERSION,
)
from .websocket_client import PandaBreathClient

_LOGGER = logging.getLogger(__name__)


class PandaBreathCoordinator(DataUpdateCoordinator):
    """Manages all communication with the Panda Breath device."""

    def __init__(self, hass: HomeAssistant, client: PandaBreathClient) -> None:
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=UPDATE_INTERVAL),
        )
        self.client = client
        self._realtime_data: dict[str, Any] = {}
        self._stop_event = asyncio.Event()
        self._listener_task: asyncio.Task | None = None

    async def _async_update_data(self) -> dict[str, Any]:
        """
        Called every UPDATE_INTERVAL seconds.
        Reconnects to get the full fresh state.
        """
        try:
            raw = await self.client.fetch_state()
            settings = raw.get("settings", {})

            state = {
                KEY_WORK_ON: bool(settings.get(KEY_WORK_ON, True)),
                KEY_WORK_MODE: settings.get(KEY_WORK_MODE, 1),
                KEY_SET_TEMP: settings.get(KEY_SET_TEMP, 45),
                KEY_FILTER_TEMP: settings.get(KEY_FILTER_TEMP, 30),
                KEY_HOTBED_TEMP: settings.get(KEY_HOTBED_TEMP, 80),
                KEY_FW_VERSION: settings.get(KEY_FW_VERSION, "unknown"),
                # Keep realtime temp if available
                KEY_WAREHOUSE_TEMPER: self._realtime_data.get(
                    KEY_WAREHOUSE_TEMPER,
                    settings.get(KEY_WAREHOUSE_TEMPER, 0)
                ),
            }
            _LOGGER.debug("Updated state: %s", state)
            return state

        except Exception as e:
            raise UpdateFailed(f"Error communicating with Panda Breath: {e}") from e

    def _on_realtime_message(self, data: dict) -> None:
        """Called by the persistent listener for every incoming message."""
        settings = data.get("settings", {})
        if KEY_WAREHOUSE_TEMPER in settings:
            self._realtime_data[KEY_WAREHOUSE_TEMPER] = settings[KEY_WAREHOUSE_TEMPER]
            # Update coordinator data in place so sensor picks it up immediately
            if self.data:
                self.data[KEY_WAREHOUSE_TEMPER] = settings[KEY_WAREHOUSE_TEMPER]
                self.async_set_updated_data(dict(self.data))

    async def start_listener(self) -> None:
        """Start the persistent WebSocket listener for real-time updates."""
        self._stop_event.clear()
        self._listener_task = self.hass.async_create_task(
            self.client.listen(self._on_realtime_message, self._stop_event)
        )
        _LOGGER.debug("Started real-time listener")

    async def stop_listener(self) -> None:
        """Stop the persistent WebSocket listener."""
        self._stop_event.set()
        if self._listener_task:
            self._listener_task.cancel()
            try:
                await self._listener_task
            except asyncio.CancelledError:
                pass
        _LOGGER.debug("Stopped real-time listener")

    async def send_settings(self, members: dict[str, Any]) -> None:
        """Send a settings command to the device."""
        await self.client.send_command("settings", members)
        # Refresh state after command
        await self.async_request_refresh()
