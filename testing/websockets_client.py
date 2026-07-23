from __future__ import annotations

import asyncio
import json
from dataclasses import dataclass
from typing import Any

try:
    from websockets.asyncio.client import connect
except ImportError:
    connect = None


def _require_websockets() -> None:
    if connect is None:
        raise RuntimeError("websockets is required for WebSocket communication.")


@dataclass(frozen=True)
class WebSocketChannel:
    name: str
    protocol: str
    host: str
    port: int
    path: str
    headers: dict[str, str] | None = None

    @property
    def url(self) -> str:
        path = self.path if self.path.startswith("/") else f"/{self.path}"
        return f"{self.protocol}://{self.host}:{self.port}{path}"

    async def exchange_async(
        self,
        message: str | bytes | dict[str, Any],
        timeout_seconds: float = 10,
    ) -> str | bytes:
        _require_websockets()
        payload = json.dumps(message) if isinstance(message, dict) else message
        async with connect(self.url, additional_headers=self.headers) as websocket:
            await websocket.send(payload)
            return await asyncio.wait_for(websocket.recv(), timeout=timeout_seconds)

    def exchange(
        self,
        message: str | bytes | dict[str, Any],
        timeout_seconds: float = 10,
    ) -> str | bytes:
        return asyncio.run(self.exchange_async(message, timeout_seconds))

    async def send_async(self, message: str | bytes | dict[str, Any]) -> None:
        _require_websockets()
        payload = json.dumps(message) if isinstance(message, dict) else message
        async with connect(self.url, additional_headers=self.headers) as websocket:
            await websocket.send(payload)

    def send(self, message: str | bytes | dict[str, Any]) -> None:
        asyncio.run(self.send_async(message))

    async def receive_async(self, timeout_seconds: float = 10) -> str | bytes:
        _require_websockets()
        async with connect(self.url, additional_headers=self.headers) as websocket:
            return await asyncio.wait_for(websocket.recv(), timeout=timeout_seconds)

    def receive(self, timeout_seconds: float = 10) -> str | bytes:
        return asyncio.run(self.receive_async(timeout_seconds))


class WebSocketFactory:
    @staticmethod
    def create(
        name: str,
        config: dict[str, Any],
        host: str | None = None,
    ) -> WebSocketChannel:
        resolved_host = host or config.get("host")
        if not resolved_host:
            raise ValueError(f"WebSocket '{name}' needs an operational IP or host")
        return WebSocketChannel(
            name=name,
            protocol=config.get("protocol", "wss"),
            host=resolved_host,
            port=config.get("port", 8080),
            path=config.get("path", "/"),
            headers=config.get("headers"),
        )
