import pytest
import jwt
import json
from types import SimpleNamespace

from app.auth import CognitoTokenValidator


def test_get_jwks_fetches_from_urlopen_when_cache_empty(monkeypatch, app):
    validator = CognitoTokenValidator(
        region="us-east-1",
        user_pool_id="pool123",
        client_id="client123",
    )

    fake_jwks = {"keys": [{"kid": "abc123"}]}

    class MockResponse:
        def read(self):
            return json.dumps(fake_jwks).encode("utf-8")

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc_val, exc_tb):
            pass

    monkeypatch.setattr("app.auth.cache.get", lambda key: None)
    saved = {}
    monkeypatch.setattr("app.auth.cache.set", lambda key, value: saved.update({key: value}))
    monkeypatch.setattr("app.auth.urlopen", lambda url: MockResponse())

    with app.app_context():
        jwks = validator.get_jwks()

    assert jwks == fake_jwks
    assert saved["cognito:jwks"] == fake_jwks
    



def test_get_jwks_returns_cached_value_without_calling_urlopen(monkeypatch, app):
    validator = CognitoTokenValidator(
        region="us-east-1",
        user_pool_id="pool123",
        client_id="client123",
    )

    cached_jwks = {"keys": [{"kid": "cached-key"}]}

    monkeypatch.setattr("app.auth.cache.get", lambda key: cached_jwks)

    def fail_urlopen(url):
        raise AssertionError("urlopen should not be called when JWKS is cached")

    monkeypatch.setattr("app.auth.urlopen", fail_urlopen)

    with app.app_context():
        jwks = validator.get_jwks()

    assert jwks == cached_jwks
    


def test_validate_token_raises_error_when_matching_jwk_not_found(monkeypatch):
    validator = CognitoTokenValidator(
        region="us-east-1",
        user_pool_id="pool123",
        client_id="client123",
    )

    fake_jwks = {"keys": [{"kid": "different-kid"}]}

    monkeypatch.setattr(validator, "get_jwks", lambda: fake_jwks)
    monkeypatch.setattr("app.auth.jwt.get_unverified_header", lambda token: {"kid": "wanted-kid"})

    with pytest.raises(jwt.InvalidTokenError, match="Unable to find matching JWKS key"):
        validator.validate_token("bad-token")


def test_protected_route_returns_403_when_no_token_provided(client):
    response = client.post(
        "/trade/buy",
        json={"portfolio_id": 1, "ticker": "AAPL", "quantity": 5},
    )

    assert response.status_code == 403
    assert response.json["error"] == "Forbidden"
    assert response.json["detail"] == "Missing or invalid Authorization header."


def test_protected_route_returns_403_when_token_is_expired(client, monkeypatch):
    class MockValidator:
        def validate_token(self, token):
            raise jwt.ExpiredSignatureError("Token expired")

    monkeypatch.setattr("app.auth._build_validator", lambda: MockValidator())

    response = client.post(
        "/trade/buy",
        json={"portfolio_id": 1, "ticker": "AAPL", "quantity": 5},
        headers={"Authorization": "Bearer expired-token"},
    )

    assert response.status_code == 403
    assert response.json["error"] == "Forbidden"
    assert response.json["detail"] == "Token has expired."


def test_protected_route_returns_403_when_token_signature_is_invalid(client, monkeypatch):
    class MockValidator:
        def validate_token(self, token):
            raise jwt.InvalidTokenError("Signature verification failed")

    monkeypatch.setattr("app.auth._build_validator", lambda: MockValidator())

    response = client.post(
        "/trade/buy",
        json={"portfolio_id": 1, "ticker": "AAPL", "quantity": 5},
        headers={"Authorization": "Bearer invalid-token"},
    )

    assert response.status_code == 403
    assert response.json["error"] == "Forbidden"
    assert response.json["detail"] == "Invalid token: Signature verification failed"


def test_protected_route_allows_access_with_valid_token(client, monkeypatch):
    class MockValidator:
        def validate_token(self, token):
            return {"username": "admin"}

    monkeypatch.setattr("app.auth._build_validator", lambda: MockValidator())

    monkeypatch.setattr(
        "app.service.portfolio_service.get_portfolio_by_id",
        lambda pid: type("Portfolio", (), {"id": pid, "owner": "admin"})(),
    )
    monkeypatch.setattr(
        "app.service.portfolio_service.ensure_can_manage_portfolio",
        lambda portfolio, username: None,
    )
    monkeypatch.setattr(
        "app.service.trade_service.execute_purchase_order",
        lambda portfolio_id, ticker, quantity: None,
    )

    response = client.post(
        "/trade/buy",
        json={"portfolio_id": 1, "ticker": "AAPL", "quantity": 5},
        headers={"Authorization": "Bearer valid-token"},
    )

    assert response.status_code == 201
    assert response.json["message"] == "Purchase order executed successfully"