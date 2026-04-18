import pytest

from app.db import db
from app.models.Investment import Investment
from app.models.Portfolio import Portfolio
from app.models.Security import Security
from app.models.User import User
from app.service.trade_service import (
    TradeExecutionException,
    InsufficientFundsError,
    execute_purchase_order,
    liquidate_investment,
)


class MockQuote:
    def __init__(self, price, issuer="Mock Issuer"):
        self.price = price
        self.issuer = issuer


@pytest.fixture
def trade_setup(app):
    user = User(
        username="trade_user",
        password="pw",
        firstname="Trade",
        lastname="User",
        balance=1000.0,
    )
    db.session.add(user)
    db.session.flush()

    portfolio = Portfolio(
        name="Trade Portfolio",
        description="For trade service tests",
        user=user,
    )
    db.session.add(portfolio)
    db.session.commit()

    return user, portfolio


def test_execute_purchase_order_invalid_parameters(app):
    with pytest.raises(TradeExecutionException):
        execute_purchase_order(None, "AAPL", 1)

    with pytest.raises(TradeExecutionException):
        execute_purchase_order(1, "", 1)

    with pytest.raises(TradeExecutionException):
        execute_purchase_order(1, "AAPL", 0)


def test_execute_purchase_order_portfolio_not_found(app):
    with pytest.raises(TradeExecutionException):
        execute_purchase_order(9999, "AAPL", 1)


def test_execute_purchase_order_invalid_ticker(app, monkeypatch, trade_setup):
    monkeypatch.setattr(
        "app.service.trade_service.get_quote",
        lambda ticker: None,
    )

    _, portfolio = trade_setup

    with pytest.raises(TradeExecutionException):
        execute_purchase_order(portfolio.id, "BAD", 1)


def test_execute_purchase_order_insufficient_funds(app, monkeypatch, trade_setup):
    monkeypatch.setattr(
        "app.service.trade_service.get_quote",
        lambda ticker: MockQuote(price=1000.0, issuer="Apple Inc."),
    )

    _, portfolio = trade_setup

    with pytest.raises(InsufficientFundsError):
        execute_purchase_order(portfolio.id, "AAPL", 2)


def test_execute_purchase_order_creates_new_investment_and_transaction(app, monkeypatch, trade_setup):
    monkeypatch.setattr(
        "app.service.trade_service.get_quote",
        lambda ticker: MockQuote(price=100.0, issuer="Apple Inc."),
    )

    user, portfolio = trade_setup

    execute_purchase_order(portfolio.id, "AAPL", 2)
    db.session.commit()

    db.session.refresh(user)
    db.session.refresh(portfolio)

    investment = next((inv for inv in portfolio.investments if inv.ticker == "AAPL"), None)

    assert investment is not None
    assert investment.quantity == 2
    assert user.balance == 800.0


def test_execute_purchase_order_updates_existing_investment(app, monkeypatch, trade_setup):
    monkeypatch.setattr(
        "app.service.trade_service.get_quote",
        lambda ticker: MockQuote(price=50.0, issuer="Apple Inc."),
    )

    user, portfolio = trade_setup
    portfolio.investments.append(Investment(ticker="AAPL", quantity=3))
    db.session.commit()

    execute_purchase_order(portfolio.id, "AAPL", 2)
    db.session.commit()

    db.session.refresh(user)
    db.session.refresh(portfolio)

    investment = next((inv for inv in portfolio.investments if inv.ticker == "AAPL"), None)

    assert investment.quantity == 5
    assert user.balance == 900.0


def test_liquidate_investment_invalid_parameters(app):
    with pytest.raises(TradeExecutionException):
        liquidate_investment(None, "AAPL", 1)

    with pytest.raises(TradeExecutionException):
        liquidate_investment(1, "", 1)

    with pytest.raises(TradeExecutionException):
        liquidate_investment(1, "AAPL", 0)


def test_liquidate_investment_quote_not_found(app, monkeypatch):
    monkeypatch.setattr(
        "app.service.trade_service.get_quote",
        lambda ticker: None,
    )

    with pytest.raises(TradeExecutionException):
        liquidate_investment(1, "AAPL", 1)


def test_liquidate_investment_portfolio_not_found(app, monkeypatch):
    monkeypatch.setattr(
        "app.service.trade_service.get_quote",
        lambda ticker: MockQuote(price=100.0, issuer="Apple Inc."),
    )

    with pytest.raises(TradeExecutionException):
        liquidate_investment(9999, "AAPL", 1)


def test_liquidate_investment_missing_investment(app, monkeypatch, trade_setup):
    monkeypatch.setattr(
        "app.service.trade_service.get_quote",
        lambda ticker: MockQuote(price=100.0, issuer="Apple Inc."),
    )

    _, portfolio = trade_setup

    with pytest.raises(TradeExecutionException):
        liquidate_investment(portfolio.id, "AAPL", 1)


def test_liquidate_investment_insufficient_quantity(app, monkeypatch, trade_setup):
    monkeypatch.setattr(
        "app.service.trade_service.get_quote",
        lambda ticker: MockQuote(price=100.0, issuer="Apple Inc."),
    )

    _, portfolio = trade_setup
    portfolio.investments.append(Investment(ticker="AAPL", quantity=1))
    db.session.commit()

    with pytest.raises(TradeExecutionException):
        liquidate_investment(portfolio.id, "AAPL", 5)


def test_liquidate_investment_partial_sale(app, monkeypatch, trade_setup):
    monkeypatch.setattr(
        "app.service.trade_service.get_quote",
        lambda ticker: MockQuote(price=100.0, issuer="Apple Inc."),
    )

    user, portfolio = trade_setup
    portfolio.investments.append(Investment(ticker="AAPL", quantity=5))
    db.session.commit()

    liquidate_investment(portfolio.id, "AAPL", 2)
    db.session.commit()

    db.session.refresh(user)
    db.session.refresh(portfolio)

    investment = next((inv for inv in portfolio.investments if inv.ticker == "AAPL"), None)

    assert investment is not None
    assert investment.quantity == 3
    assert user.balance == 1200.0


def test_liquidate_investment_full_sale_removes_investment(app, monkeypatch, trade_setup):
    monkeypatch.setattr(
        "app.service.trade_service.get_quote",
        lambda ticker: MockQuote(price=100.0, issuer="Apple Inc."),
    )

    user, portfolio = trade_setup
    portfolio.investments.append(Investment(ticker="AAPL", quantity=2))
    db.session.commit()

    liquidate_investment(portfolio.id, "AAPL", 2)
    db.session.commit()

    db.session.refresh(user)
    db.session.refresh(portfolio)

    investment = next((inv for inv in portfolio.investments if inv.ticker == "AAPL"), None)

    assert investment is None
    assert user.balance == 1200.0