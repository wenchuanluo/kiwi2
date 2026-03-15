import pytest

from app.db import db
from app.models.Portfolio import Portfolio
from app.models.User import User
from app.service import portfolio_service
from app.service.portfolio_service import PortfolioAuthorizationError


def build_auth_headers(username: str) -> dict:
    return {"Authorization": f"Bearer {username}-token"}


def mock_auth_as(monkeypatch, username: str):
    class MockValidator:
        def validate_token(self, token):
            return {"username": username}

    monkeypatch.setattr("app.auth._build_validator", lambda: MockValidator())


@pytest.fixture
def authorization_setup(app):
    owner = User(
        username="owner_user",
        password="pw",
        firstname="Owner",
        lastname="User",
        balance=1000.0,
    )
    viewer = User(
        username="viewer_user",
        password="pw",
        firstname="Viewer",
        lastname="User",
        balance=1000.0,
    )
    manager = User(
        username="manager_user",
        password="pw",
        firstname="Manager",
        lastname="User",
        balance=1000.0,
    )
    outsider = User(
        username="outsider_user",
        password="pw",
        firstname="Outsider",
        lastname="User",
        balance=1000.0,
    )

    db.session.add_all([owner, viewer, manager, outsider])
    db.session.flush()

    portfolio = Portfolio(
        name="Test Portfolio",
        description="Authorization test portfolio",
        user=owner,
    )
    db.session.add(portfolio)
    db.session.flush()

    portfolio_service.grant_portfolio_access(portfolio.id, viewer.username, "viewer")
    portfolio_service.grant_portfolio_access(portfolio.id, manager.username, "manager")
    db.session.commit()

    return {
        "owner": owner,
        "viewer": viewer,
        "manager": manager,
        "outsider": outsider,
        "portfolio": portfolio,
    }


def test_owner_can_perform_all_operations_on_own_portfolio(authorization_setup):
    owner = authorization_setup["owner"]
    portfolio = authorization_setup["portfolio"]

    assert portfolio_service.can_view_portfolio(portfolio, owner.username) is True
    assert portfolio_service.can_manage_portfolio(portfolio, owner.username) is True

    portfolio_service.ensure_can_view_portfolio(portfolio, owner.username)
    portfolio_service.ensure_can_manage_portfolio(portfolio, owner.username)
    portfolio_service.ensure_is_portfolio_owner(portfolio, owner.username)


def test_viewer_can_view_but_cannot_execute_trades(authorization_setup):
    viewer = authorization_setup["viewer"]
    portfolio = authorization_setup["portfolio"]

    assert portfolio_service.can_view_portfolio(portfolio, viewer.username) is True
    assert portfolio_service.can_manage_portfolio(portfolio, viewer.username) is False

    portfolio_service.ensure_can_view_portfolio(portfolio, viewer.username)

    with pytest.raises(PortfolioAuthorizationError) as exc_info:
        portfolio_service.ensure_can_manage_portfolio(portfolio, viewer.username)

    assert str(exc_info.value) == "You do not have permission to trade on this portfolio."


def test_manager_can_execute_trades_but_is_not_owner(authorization_setup):
    manager = authorization_setup["manager"]
    portfolio = authorization_setup["portfolio"]

    assert portfolio_service.can_view_portfolio(portfolio, manager.username) is True
    assert portfolio_service.can_manage_portfolio(portfolio, manager.username) is True

    portfolio_service.ensure_can_view_portfolio(portfolio, manager.username)
    portfolio_service.ensure_can_manage_portfolio(portfolio, manager.username)

    with pytest.raises(PortfolioAuthorizationError) as exc_info:
        portfolio_service.ensure_is_portfolio_owner(portfolio, manager.username)

    assert str(exc_info.value) == "Only the portfolio owner can perform this action."


def test_user_with_no_access_receives_authorization_error(authorization_setup):
    outsider = authorization_setup["outsider"]
    portfolio = authorization_setup["portfolio"]

    assert portfolio_service.can_view_portfolio(portfolio, outsider.username) is False
    assert portfolio_service.can_manage_portfolio(portfolio, outsider.username) is False

    with pytest.raises(PortfolioAuthorizationError) as exc_info:
        portfolio_service.ensure_can_view_portfolio(portfolio, outsider.username)

    assert str(exc_info.value) == "You do not have permission to view this portfolio."

    with pytest.raises(PortfolioAuthorizationError) as exc_info:
        portfolio_service.ensure_can_manage_portfolio(portfolio, outsider.username)

    assert str(exc_info.value) == "You do not have permission to trade on this portfolio."


def test_viewer_gets_403_on_trade_route(client, monkeypatch, authorization_setup):
    viewer = authorization_setup["viewer"]
    portfolio = authorization_setup["portfolio"]

    mock_auth_as(monkeypatch, viewer.username)

    monkeypatch.setattr(
        "app.service.trade_service.execute_purchase_order",
        lambda portfolio_id, ticker, quantity: None,
    )

    response = client.post(
        "/trade/buy",
        json={"portfolio_id": portfolio.id, "ticker": "AAPL", "quantity": 1},
        headers=build_auth_headers(viewer.username),
    )

    assert response.status_code == 403
    assert response.json["error"] == "Forbidden"
    assert response.json["detail"] == "You do not have permission to trade on this portfolio."


def test_manager_can_access_trade_route(client, monkeypatch, authorization_setup):
    manager = authorization_setup["manager"]
    portfolio = authorization_setup["portfolio"]

    mock_auth_as(monkeypatch, manager.username)

    monkeypatch.setattr(
        "app.service.trade_service.execute_purchase_order",
        lambda portfolio_id, ticker, quantity: None,
    )

    response = client.post(
        "/trade/buy",
        json={"portfolio_id": portfolio.id, "ticker": "AAPL", "quantity": 1},
        headers=build_auth_headers(manager.username),
    )

    assert response.status_code == 201
    assert response.json["message"] == "Purchase order executed successfully"


def test_outsider_gets_403_on_trade_route(client, monkeypatch, authorization_setup):
    outsider = authorization_setup["outsider"]
    portfolio = authorization_setup["portfolio"]

    mock_auth_as(monkeypatch, outsider.username)

    monkeypatch.setattr(
        "app.service.trade_service.execute_purchase_order",
        lambda portfolio_id, ticker, quantity: None,
    )

    response = client.post(
        "/trade/buy",
        json={"portfolio_id": portfolio.id, "ticker": "AAPL", "quantity": 1},
        headers=build_auth_headers(outsider.username),
    )

    assert response.status_code == 403
    assert response.json["error"] == "Forbidden"
    assert response.json["detail"] == "You do not have permission to trade on this portfolio."