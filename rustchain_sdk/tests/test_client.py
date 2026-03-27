from rustchain.client import RustChainClient

class DummyResponse:
    def __init__(self, status_code=200, data=None, text=""):
        self.status_code = status_code
        self._data = data or {}
        self.text = text
    def json(self):
        return self._data

class DummyHTTP:
    def __init__(self):
        self.calls = []
    def get(self, path, params=None):
        self.calls.append(("GET", path, params))
        return DummyResponse(200, {"ok": True, "path": path})
    def post(self, path, json=None):
        self.calls.append(("POST", path, json))
        return DummyResponse(200, {"ok": True, "path": path, "payload": json})


def test_health():
    c = RustChainClient()
    c._client = DummyHTTP()
    assert c.health()["ok"] is True


def test_epoch():
    c = RustChainClient()
    c._client = DummyHTTP()
    assert c.epoch()["path"] == "/epoch"


def test_miners():
    c = RustChainClient()
    c._client = DummyHTTP()
    assert c.miners()["path"] == "/api/miners"


def test_balance():
    c = RustChainClient()
    c._client = DummyHTTP()
    assert c.balance("wallet123")["path"] == "/balance/wallet123"


def test_transfer():
    c = RustChainClient()
    c._client = DummyHTTP()
    out = c.transfer("a", "b", 1, "sig")
    assert out["payload"]["to"] == "b"


def test_attestation():
    c = RustChainClient()
    c._client = DummyHTTP()
    assert c.attestation_status("miner1")["path"] == "/withdraw/history/miner1"


def test_explorer_blocks():
    c = RustChainClient()
    c._client = DummyHTTP()
    assert c.explorer.blocks()["path"] == "/api/stats"


def test_explorer_transactions():
    c = RustChainClient()
    c._client = DummyHTTP()
    assert c.explorer.transactions()["path"] == "/metrics"
