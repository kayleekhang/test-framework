import asyncio
from dataclasses import dataclass
from typing import Any
from urllib.parse import urlencode

try:
    import httpx
except ImportError:
    httpx = None


def _require_httpx():
    if httpx is None:
        raise RuntimeError("httpx is required to call API endpoints.")


@dataclass(frozen=True)
class Endpoint:
    protocol: str
    host: str
    port: int
    path: str
    method: str = "GET"
    query: dict[str, str] | None = None
    headers: dict[str, str] | None = None
    body: dict[str, Any] | str | bytes | None = None

    @property
    def url(self) -> str:
        query = f"?{urlencode(self.query)}" if self.query else ""
        return f"{self.protocol}://{self.host}:{self.port}{self.path}{query}"


@dataclass(frozen=True)
class APIResponse:
    endpoint_name: str
    url: str
    status_code: int | None
    body: str | None = None
    error: str | None = None

    @property
    def ok(self) -> bool:
        return self.error is None and self.status_code is not None and self.status_code < 400


class API:
    def __init__(self, endpoints: dict[str, Endpoint], base_headers: dict[str, str] | None = None):
        self.endpoints = endpoints
        self.base_headers = base_headers or {}

    def endpoint(self, name: str) -> Endpoint:
        return self.endpoints[name]

    def request(self, name: str, timeout_seconds: int = 10) -> APIResponse:
        _require_httpx()
        endpoint = self.endpoint(name)
        headers = self._headers_for(endpoint)

        try:
            with httpx.Client(timeout=timeout_seconds) as client:
                response = client.request(
                    method=endpoint.method,
                    url=endpoint.url,
                    headers=headers,
                    content=endpoint.body if isinstance(endpoint.body, (bytes, str)) else None,
                    json=endpoint.body if isinstance(endpoint.body, dict) else None,
                )
                return APIResponse(
                    endpoint_name=name,
                    url=endpoint.url,
                    status_code=response.status_code,
                    body=response.text,
                )
        except Exception as exc:
            return APIResponse(
                endpoint_name=name,
                url=endpoint.url,
                status_code=None,
                error=str(exc),
            )

    def request_many(
        self,
        names: list[str] | None = None,
        timeout_seconds: int = 10,
    ) -> dict[str, APIResponse]:
        return asyncio.run(self.request_many_async(names, timeout_seconds=timeout_seconds))

    async def request_async(
        self,
        name: str,
        client: Any | None = None,
        timeout_seconds: int = 10,
    ) -> APIResponse:
        _require_httpx()
        endpoint = self.endpoint(name)
        headers = self._headers_for(endpoint)

        try:
            if client is None:
                async with httpx.AsyncClient(timeout=timeout_seconds) as async_client:
                    return await self.request_async(name, async_client, timeout_seconds)

            response = await client.request(
                method=endpoint.method,
                url=endpoint.url,
                headers=headers,
                content=endpoint.body if isinstance(endpoint.body, (bytes, str)) else None,
                json=endpoint.body if isinstance(endpoint.body, dict) else None,
            )
            return APIResponse(
                endpoint_name=name,
                url=endpoint.url,
                status_code=response.status_code,
                body=response.text,
            )
        except Exception as exc:
            return APIResponse(
                endpoint_name=name,
                url=endpoint.url,
                status_code=None,
                error=str(exc),
            )

    async def request_many_async(
        self,
        names: list[str] | None = None,
        timeout_seconds: int = 10,
    ) -> dict[str, APIResponse]:
        _require_httpx()
        endpoint_names = names or list(self.endpoints)

        async with httpx.AsyncClient(timeout=timeout_seconds) as client:
            responses = await asyncio.gather(
                *(self.request_async(name, client, timeout_seconds) for name in endpoint_names)
            )

        return {response.endpoint_name: response for response in responses}

    def _headers_for(self, endpoint: Endpoint) -> dict[str, str]:
        headers = {**self.base_headers, **(endpoint.headers or {})}
        if isinstance(endpoint.body, dict):
            headers.setdefault("Content-Type", "application/json")
        return headers
