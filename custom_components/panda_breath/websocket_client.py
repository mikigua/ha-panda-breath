"""WebSocket client for Panda Breath."""
from __future__ import annotations

import asyncio
import json
import logging
from typing import Any, Callable

import websockets
from websockets.exceptions import ConnectionClosed, WebSocketException

from .const import WS_PATH, WS_TIMEOUT

_LOGGER = logging.getLogger(__name__)


class PandaBreathClient:
    """WebSocket client to communicate with Panda Breath."""

    def __init__(self, host: str, port: int = 80) -> None:
        self._host = host
        self._port = port
        self._ws = None
        self._listeners: list[Callable[[dict], None]] = []

    @property
    def uri(self) -> str:
        return f"ws://{self._host}:{self._port}{WS_PATH}"

    def add_listener(self, callback: Callable[[dict], None]) -> None:
        self._listeners.append(callback)

    def remove_listener(self, callback: Callable[[dict], None]) -> None:
        self._listeners.remove(callback)

    def _notify_listeners(self, data: dict) -> None:
        for cb in self._listeners:
            try:
                cb(data)
            except Exception as e:
                _LOGGER.error("Error in listener callback: %s", e)

    async def fetch_state(self) -> dict[str, Any]:
        """
        Connect to Panda Breath, receive the initial full state message,
        then close the connection. Returns the parsed state dict.
        """
        try:
            async with websockets.connect(
                self.uri,
                open_timeout=WS_TIMEOUT,
                close_timeout=WS_TIMEOUT,
            ) as ws:
                _LOGGER.debug("Connected to %s, waiting for state...", self.uri)
                raw = await asyncio.wait_for(ws.recv(), timeout=WS_TIMEOUT)
                data = json.loads(raw)
                _LOGGER.debug("Received state: %s", data)
                return data
        except (ConnectionClosed, WebSocketException, OSError, asyncio.TimeoutError) as e:
            _LOGGER.warning("Failed to fetch state from %s: %s", self.uri, e)
            raise

    async def send_command(self, root: str, members: dict[str, Any]) -> None:
        """
        Connect, send a command, then close.
        This mirrors ws_send_data() from the web UI.
        """
        payload = json.dumps({root: members})
        try:
            async with websockets.connect(
                self.uri,
                open_timeout=WS_TIMEOUT,
                close_timeout=WS_TIMEOUT,
            ) as ws:
                _LOGGER.debug("Sending command: %s", payload)
                await ws.send(payload)
                # Wait briefly to allow device to process
                await asyncio.sleep(0.5)
        except (ConnectionClosed, WebSocketException, OSError, asyncio.TimeoutError) as e:
            _LOGGER.warning("Failed to send command to %s: %s", self.uri, e)
            raise

    async def listen(self, on_message: Callable[[dict], None], stop_event: asyncio.Event) -> None:
        """
        Keep a persistent WebSocket connection open and call on_message
        for every message received (e.g. periodic warehouse_temper updates).
        Reconnects automatically if the connection drops.
        """
        from .const import WS_RECONNECT_INTERVAL
        while not stop_event.is_set():
            try:
                async with websockets.connect(
                    self.uri,
                    open_timeout=WS_TIMEOUT,
                ) as ws:
                    _LOGGER.debug("Persistent listener connected to %s", self.uri)
                    while not stop_event.is_set():
                        try:
                            raw = await asyncio.wait_for(ws.recv(), timeout=30)
                            data = json.loads(raw)
                            on_message(data)
                        except asyncio.TimeoutError:
                            # No message in 30s, just keep waiting
                            continue
            except (ConnectionClosed, WebSocketException, OSError) as e:
                _LOGGER.warning("Listener connection lost: %s. Reconnecting in %ds...", e, WS_RECONNECT_INTERVAL)
                await asyncio.sleep(WS_RECONNECT_INTERVAL)

    async def test_connection(self) -> bool:
        """Test if the Panda Breath is reachable."""
        try:
            await self.fetch_state()
            return True
        except Exception:
            return False
