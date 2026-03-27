from rustchain.models import HealthResponse, EpochResponse, MinersResponse, BalanceResponse


def test_health_response_model():
    r = HealthResponse(data={"status": "ok"})
    assert r.data["status"] == "ok"


def test_epoch_response_model():
    r = EpochResponse(data={"epoch": 1})
    assert r.data["epoch"] == 1


def test_miners_response_model():
    r = MinersResponse(data=[{"id": "m1"}])
    assert r.data[0]["id"] == "m1"


def test_balance_response_model():
    r = BalanceResponse(data={"balance": 100})
    assert r.data["balance"] == 100
