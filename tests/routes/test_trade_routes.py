import pytest

from app.service.trade_service import TradeExecutionException


def mock_auth(monkeypatch):
    class MockValidator:
        def validate_token(self, token):
            return {"username": "admin"}

    monkeypatch.setattr("app.auth._build_validator", lambda: MockValidator())


def auth_headers():
    return {"Authorization": "Bearer fake-token"}


def test_buy_trade_success(client, monkeypatch):
    mock_auth(monkeypatch)

    monkeypatch.setattr(
        "app.service.portfolio_service.get_portfolio_by_id",
        lambda pid: type("Portfolio", (), {"id": pid, "owner": "admin"})(),
    )
    monkeypatch.setattr(
        "app.service.portfolio_service.ensure_can_manage_portfolio",
        lambda portfolio, user: None,
    )
    monkeypatch.setattr(
        "app.service.trade_service.execute_purchase_order",
        lambda portfolio_id, ticker, quantity: None,
    )

    response = client.post(
        "/trade/buy",
        json={"portfolio_id": 1, "ticker": "AAPL", "quantity": 5},
        headers=auth_headers(),
    )

    assert response.status_code == 201
    assert response.json["message"] == "Purchase order executed successfully"


def test_sell_trade_success(client, monkeypatch):
    mock_auth(monkeypatch)

    monkeypatch.setattr(
        "app.service.portfolio_service.get_portfolio_by_id",
        lambda pid: type("Portfolio", (), {"id": pid, "owner": "admin"})(),
    )
    monkeypatch.setattr(
        "app.service.portfolio_service.ensure_can_manage_portfolio",
        lambda portfolio, user: None,
    )
    monkeypatch.setattr(
        "app.service.trade_service.liquidate_investment",
        lambda portfolio_id, ticker, quantity: None,
    )

    response = client.post(
        "/trade/sell",
        json={"portfolio_id": 1, "ticker": "AAPL", "quantity": 2},
        headers=auth_headers(),
    )

    assert response.status_code == 200
    assert response.json["message"] == "Investment liquidated successfully"


def test_buy_trade_portfolio_not_found(client, monkeypatch):
    mock_auth(monkeypatch)

    monkeypatch.setattr(
        "app.service.portfolio_service.get_portfolio_by_id",
        lambda pid: None,
    )

    response = client.post(
        "/trade/buy",
        json={"portfolio_id": 99, "ticker": "AAPL", "quantity": 5},
        headers=auth_headers(),
    )

    assert response.status_code == 404
    assert response.json["error"] == "Portfolio 99 not found"

def test_buy_trade_validation_error(client, monkeypatch):
    mock_auth(monkeypatch)

    response = client.post(
        "/trade/buy",
        json={"portfolio_id": 1, "ticker": "", "quantity": 5},
        headers=auth_headers(),
    )

    assert response.status_code == 422
    assert response.json["error"] == "Validation Error"


def test_buy_trade_execution_exception(client, monkeypatch):
    mock_auth(monkeypatch)

    monkeypatch.setattr(
        "app.service.portfolio_service.get_portfolio_by_id",
        lambda pid: type("Portfolio", (), {"id": pid, "owner": "admin"})(),
    )
    monkeypatch.setattr(
        "app.service.portfolio_service.ensure_can_manage_portfolio",
        lambda portfolio, user: None,
    )

    def mock_execute(*args, **kwargs):
        raise TradeExecutionException("Trade failed")

    monkeypatch.setattr(
        "app.service.trade_service.execute_purchase_order",
        mock_execute,
    )

    response = client.post(
        "/trade/buy",
        json={"portfolio_id": 1, "ticker": "AAPL", "quantity": 5},
        headers=auth_headers(),
    )

    assert response.status_code == 400
    assert response.json["error"] == "Bad Request"
    assert response.json["detail"] == "Trade failed"