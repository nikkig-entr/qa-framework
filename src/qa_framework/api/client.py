"""Async API client with retry, logging, and validation."""

from __future__ import annotations

import time
from contextlib import asynccontextmanager
from typing import Any, Generic, TypeVar, get_args, get_origin

import httpx
import respx
from pydantic import BaseModel, ValidationError
from tenacity import retry, stop_after_attempt, wait_exponential
from typing_extensions import AsyncGenerator

from ..config import get_settings
from ..logging import LogContext, get_logger

T = TypeVar("T", bound=BaseModel)

logger = get_logger(__name__)


class APIResponse(BaseModel, Generic[T]):
    """Standardized API response wrapper."""

    status_code: int
    data: T | list[Any] | None = None
    raw_data: Any = None
    headers: dict[str, str] = {}
    elapsed_ms: float = 0.0
    error: str | None = None

    @property
    def is_success(self) -> bool:
        return 200 <= self.status_code < 300

    @property
    def is_client_error(self) -> bool:
        return 400 <= self.status_code < 500

    @property
    def is_server_error(self) -> bool:
        return 500 <= self.status_code < 600


class APIClient(Generic[T]):
    """Async HTTP client with built-in retry, validation, and logging."""

    def __init__(
        self,
        base_url: str | None = None,
        timeout: float | None = None,
        headers: dict[str, str] | None = None,
        auth: httpx.Auth | None = None,
    ) -> None:
        settings = get_settings()
        self._base_url = base_url or settings.api.base_url
        self._timeout = timeout or settings.api.timeout
        self._retries = settings.api.retries
        self._backoff = settings.api.backoff_factor
        self._default_headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            **(headers or {}),
        }
        self._auth = auth
        self._client: httpx.AsyncClient | None = None
        self._log = logger.bind(base_url=self._base_url)

    @property
    def client(self) -> httpx.AsyncClient:
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(
                base_url=self._base_url,
                timeout=self._timeout,
                headers=self._default_headers,
                auth=self._auth,
                follow_redirects=True,
            )
        return self._client

    async def close(self) -> None:
        """Close the underlying HTTP client."""
        if self._client and not self._client.is_closed:
            await self._client.aclose()
            self._client = None

    async def __aenter__(self) -> APIClient[Any]:
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        await self.close()

    @asynccontextmanager
    async def mock(self) -> AsyncGenerator[respx.MockRouter, None]:
        """Context manager for mocking HTTP requests with respx."""
        with respx.mock(base_url=self._base_url, assert_all_called=False) as router:
            yield router

    def _build_response(
        self, response: httpx.Response, model: type[T] | None = None
    ) -> APIResponse[T]:
        elapsed = response.elapsed.total_seconds() * 1000
        raw_data: Any = None
        data: T | list[Any] | None = None
        error: str | None = None

        try:
            raw_data = response.json()
        except Exception:
            raw_data = response.text

        if model and raw_data is not None:
            try:
                # Handle list types (list[Model])
                origin = get_origin(model)
                args = get_args(model)
                if origin is list and args:
                    item_model = args[0]
                    data = [item_model.model_validate(item) for item in raw_data]
                else:
                    data = model.model_validate(raw_data)
            except ValidationError as e:
                error = f"Validation error: {e}"

        if response.is_error and not error:
            error = f"HTTP {response.status_code}: {response.reason_phrase}"

        return APIResponse[T](
            status_code=response.status_code,
            data=data,
            raw_data=raw_data,
            headers=dict(response.headers),
            elapsed_ms=elapsed,
            error=error,
        )

    @retry(
        wait=wait_exponential(multiplier=0.5, min=0.5, max=10),
        stop=stop_after_attempt(3),
        reraise=True,
    )
    async def request(
        self,
        method: str,
        path: str,
        *,
        params: dict[str, Any] | None = None,
        json: Any | None = None,
        data: Any | None = None,
        headers: dict[str, str] | None = None,
        model: type[T] | None = None,
        expected_status: int | list[int] | None = None,
    ) -> APIResponse[T]:
        """Make HTTP request with retry and validation."""
        url = f"{self._base_url.rstrip('/')}/{path.lstrip('/')}"
        start = time.perf_counter()

        with LogContext(method=method, url=url, params=params):
            self._log.debug("Making request")

            response = await self.client.request(
                method=method,
                url=path,
                params=params,
                json=json,
                data=data,
                headers=headers,
            )

            elapsed = (time.perf_counter() - start) * 1000
            self._log.info(
                "Request completed",
                status=response.status_code,
                elapsed_ms=round(elapsed, 2),
            )

        result = self._build_response(response, model)

        if expected_status:
            expected = [expected_status] if isinstance(expected_status, int) else expected_status
            if response.status_code not in expected:
                raise AssertionError(
                    f"Expected status {expected}, got {response.status_code}: {result.error}"
                )

        return result

    # Convenience methods
    async def get(self, path: str, **kwargs: Any) -> APIResponse[Any]:
        return await self.request("GET", path, **kwargs)

    async def post(self, path: str, **kwargs: Any) -> APIResponse[Any]:
        return await self.request("POST", path, **kwargs)

    async def put(self, path: str, **kwargs: Any) -> APIResponse[Any]:
        return await self.request("PUT", path, **kwargs)

    async def patch(self, path: str, **kwargs: Any) -> APIResponse[Any]:
        return await self.request("PATCH", path, **kwargs)

    async def delete(self, path: str, **kwargs: Any) -> APIResponse[Any]:
        return await self.request("DELETE", path, **kwargs)

    async def head(self, path: str, **kwargs: Any) -> APIResponse[Any]:
        return await self.request("HEAD", path, **kwargs)

    async def options(self, path: str, **kwargs: Any) -> APIResponse[Any]:
        return await self.request("OPTIONS", path, **kwargs)
