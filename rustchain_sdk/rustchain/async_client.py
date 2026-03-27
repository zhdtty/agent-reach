from typing import Any, Optional
import httpx
from .exceptions import APIError, NotFoundError

class AsyncRustChainClient:
    def __init__(self, base_url: str = "https://50.28.86.131", timeout: float = 10.0, verify: bool = True):
        self.base_url = base_url.rstrip("/")
        self._client = httpx.AsyncClient(base_url=self.base_url, timeout=timeout, verify=verify)

    async def _get(self, path: str, **params: Any) -> Any:
        response = await self._client.get(path, params=params or None)
        if response.status_code == 404:
            raise NotFoundError(404, path)
        if response.status_code >= 400:
            raise APIError(response.status_code, response.text)
        return response.json()

    async def _post(self, path: str, payload: Optional[dict] = None) -> Any:
        response = await self._client.post(path, json=payload or {})
        if response.status_code == 404:
            raise NotFoundError(404, path)
        if response.status_code >= 400:
            raise APIError(response.status_code, response.text)
        return response.json()

    async def health(self) -> Any:
        return await self._get("/health")

    async def epoch(self) -> Any:
        return await self._get("/epoch")

    async def miners(self) -> Any:
        return await self._get("/api/miners")

    async def balance(self, wallet_id: str) -> Any:
        return await self._get(f"/balance/{wallet_id}")

    async def transfer(self, from_: str, to: str, amount: int | float, signature: str) -> Any:
        return await self._post("/withdraw/request", {
            "from": from_,
            "to": to,
            "amount": amount,
            "signature": signature,
        })

    async def attestation_status(self, miner_id: str) -> Any:
        return await self._get(f"/withdraw/history/{miner_id}")

    async def stats(self) -> Any:
        return await self._get("/api/stats")

    async def metrics(self) -> Any:
        return await self._get("/metrics")

    async def openapi(self) -> Any:
        return await self._get("/openapi.json")

    async def blocks(self) -> Any:
        return await self.stats()

    async def transactions(self) -> Any:
        return await self.metrics()

    async def aclose(self) -> None:
        await self._client.aclose()
