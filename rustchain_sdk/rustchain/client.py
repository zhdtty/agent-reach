from typing import Any, Optional
import httpx
from .exceptions import APIError, NotFoundError

class RustChainClient:
    def __init__(self, base_url: str = "https://50.28.86.131", timeout: float = 10.0, verify: bool = True):
        self.base_url = base_url.rstrip("/")
        self._client = httpx.Client(base_url=self.base_url, timeout=timeout, verify=verify)

    def _get(self, path: str, **params: Any) -> Any:
        response = self._client.get(path, params=params or None)
        if response.status_code == 404:
            raise NotFoundError(404, path)
        if response.status_code >= 400:
            raise APIError(response.status_code, response.text)
        return response.json()

    def _post(self, path: str, payload: Optional[dict] = None) -> Any:
        response = self._client.post(path, json=payload or {})
        if response.status_code == 404:
            raise NotFoundError(404, path)
        if response.status_code >= 400:
            raise APIError(response.status_code, response.text)
        return response.json()

    def health(self) -> Any:
        return self._get("/health")

    def epoch(self) -> Any:
        return self._get("/epoch")

    def miners(self) -> Any:
        return self._get("/api/miners")

    def balance(self, wallet_id: str) -> Any:
        return self._get(f"/balance/{wallet_id}")

    def transfer(self, from_: str, to: str, amount: int | float, signature: str) -> Any:
        return self._post("/withdraw/request", {
            "from": from_,
            "to": to,
            "amount": amount,
            "signature": signature,
        })

    def attestation_status(self, miner_id: str) -> Any:
        return self._get(f"/withdraw/history/{miner_id}")

    def stats(self) -> Any:
        return self._get("/api/stats")

    def metrics(self) -> Any:
        return self._get("/metrics")

    def openapi(self) -> Any:
        return self._get("/openapi.json")

    @property
    def explorer(self) -> "ExplorerClient":
        return ExplorerClient(self)

class ExplorerClient:
    def __init__(self, client: RustChainClient):
        self.client = client

    def blocks(self) -> Any:
        return self.client.stats()

    def transactions(self) -> Any:
        return self.client.metrics()
