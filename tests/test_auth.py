import jwt


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