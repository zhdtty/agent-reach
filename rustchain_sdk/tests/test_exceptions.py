import pytest
from rustchain.exceptions import RustChainError, APIError, NotFoundError, ValidationError


def test_base_error():
    err = RustChainError("boom")
    assert str(err) == "boom"


def test_api_error_message():
    err = APIError(500, "server")
    assert "500" in str(err)
    assert "server" in str(err)


def test_not_found_error_is_api_error():
    err = NotFoundError(404, "/missing")
    assert isinstance(err, APIError)


def test_validation_error():
    err = ValidationError("bad input")
    assert str(err) == "bad input"
