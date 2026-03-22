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

LISTEN_WINDOW = 10   # seconds to stay connected per session
POLL_INTERVAL = 15   # seconds between reconnections


class PandaBreathClient:
    """WebSocket client to communicate with Panda Breath."""

    def __init__(self, host: str, port: int = 80) -> None:
        self._host = host
        self._port = port

    @property
    def uri(self) -> str:
        return f"ws://{self._host}:{self._port}{WS_PATH}"

    async def fetch_state(self) -> dict[str, Any]:
        """Connect, receive the initial full state, then close."""
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
        """Connect, send a command, then close."""
        payload = json.dumps({root: members})
        try:
            async with websockets.connect(
                self.uri,
                open_timeout=WS_TIMEOUT,
                close_timeout=WS_TIMEOUT,
            ) as ws:
                _LOGGER.debug("Sending command: %s", payload)
                await ws.send(payload)
                await asyncio.sleep(0.5)
        except (ConnectionClosed, WebSocketException, OSError, asyncio.TimeoutError) as e:
            _LOGGER.warning("Failed to send command to %s: %s", self.uri, e)
            raise

    async def listen(self, on_message: Callable[[dict], None], stop_event: asyncio.Event) -> None:
        """
        Periodically connect, collect messages for LISTEN_WINDOW seconds,
        disconnect, wait POLL_INTERVAL seconds, then repeat.
        Handles devices that close idle WebSocket connections.
        """
        while not stop_event.is_set():
            try:
                async with websockets.connect(
                    self.uri,
                    open_timeout=WS_TIMEOUT,
                ) as ws:
                    _LOGGER.debug("Listener connected to %s", self.uri)
                    deadline = asyncio.get_event_loop().time() + LISTEN_WINDOW
                    while not stop_event.is_set():
                        remaining = deadline - asyncio.get_event_loop().time()
                        if remaining <= 0:
                            break
                        try:
                            raw = await asyncio.wait_for(
                                ws.recv(), timeout=min(remaining, 5)
                            )
                            data = json.loads(raw)
                            on_message(data)
                        except asyncio.TimeoutError:
                            continue
            except (ConnectionClosed, WebSocketException, OSError) as e:
                _LOGGER.debug("Listener session ended: %s", e)

            if not stop_event.is_set():
                await asyncio.sleep(POLL_INTERVAL)

    async def test_connection(self) -> bool:
        """Test if the Panda Breath is reachable."""
        try:
            await self.fetch_state()
            return True
        except Exception:
            return False
