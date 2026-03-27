import pytest
from rustchain.async_client import AsyncRustChainClient

class DummyResponse:
    def __init__(self, status_code=200, data=None, text=""):
        self.status_code = status_code
        self._data = data or {}
        self.text = text
    def json(self):
        return self._data

class DummyHTTP:
    async def get(self, path, params=None):
        return DummyResponse(200, {"ok": True, "path": path})
    async def post(self, path, json=None):
        return DummyResponse(200, {"ok": True, "path": path, "payload": json})
    async def aclose(self):
        return None

@pytest.mark.asyncio
async def test_async_health():
    c = AsyncRustChainClient()
    c._client = DummyHTTP()
    assert (await c.health())["ok"] is True

@pytest.mark.asyncio
async def test_async_epoch():
    c = AsyncRustChainClient()
    c._client = DummyHTTP()
    assert (await c.epoch())["path"] == "/epoch"

@pytest.mark.asyncio
async def test_async_balance():
    c = AsyncRustChainClient()
    c._client = DummyHTTP()
    assert (await c.balance("wallet"))["path"] == "/balance/wallet"

@pytest.mark.asyncio
async def test_async_transfer():
    c = AsyncRustChainClient()
    c._client = DummyHTTP()
    out = await c.transfer("a","b",1,"sig")
    assert out["payload"]["from"] == "a"
