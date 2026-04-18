import pytest
from pydantic import ValidationError

from app.routes.domain.trade_schema import BuyTradeRequest, SellTradeRequest


def test_buy_trade_request_valid():
    request = BuyTradeRequest(
        portfolio_id=1,
        ticker="AAPL",
        quantity=10,
    )

    assert request.portfolio_id == 1
    assert request.ticker == "AAPL"
    assert request.quantity == 10


def test_buy_trade_request_missing_ticker_raises_validation_error():
    with pytest.raises(ValidationError):
        BuyTradeRequest(
            portfolio_id=1,
            quantity=10,
        )


def test_buy_trade_request_invalid_portfolio_id_raises_validation_error():
    with pytest.raises(ValidationError):
        BuyTradeRequest(
            portfolio_id=0,
            ticker="AAPL",
            quantity=10,
        )


def test_buy_trade_request_invalid_quantity_raises_validation_error():
    with pytest.raises(ValidationError):
        BuyTradeRequest(
            portfolio_id=1,
            ticker="AAPL",
            quantity=0,
        )


def test_sell_trade_request_valid():
    request = SellTradeRequest(
        portfolio_id=2,
        ticker="MSFT",
        quantity=5,
    )

    assert request.portfolio_id == 2
    assert request.ticker == "MSFT"
    assert request.quantity == 5


def test_sell_trade_request_missing_portfolio_id_raises_validation_error():
    with pytest.raises(ValidationError):
        SellTradeRequest(
            ticker="MSFT",
            quantity=5,
        )


def test_sell_trade_request_empty_ticker_raises_validation_error():
    with pytest.raises(ValidationError):
        SellTradeRequest(
            portfolio_id=2,
            ticker="",
            quantity=5,
        )


def test_sell_trade_request_negative_quantity_raises_validation_error():
    with pytest.raises(ValidationError):
        SellTradeRequest(
            portfolio_id=2,
            ticker="MSFT",
            quantity=-1,
        )