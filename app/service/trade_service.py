import datetime

from app.db import db
from app.models import Investment, Portfolio, Transaction, Security
from app.service.alpha_vantage_client import get_quote


class TradeExecutionException(Exception):
    pass


class InsufficientFundsError(Exception):
    pass


def execute_purchase_order(portfolio_id: int, ticker: str, quantity: int):
    """
    Execute a purchase order for a given portfolio, security ticker, and quantity.

    Args:
        portfolio_id (int): The ID of the portfolio.
        ticker (str): The ticker symbol of the security to purchase.
        quantity (int): The number of shares to purchase.

    Raises:
        TradeExecutionException: If the order parameters are invalid, or related
            portfolio/user records do not exist, or the ticker cannot be resolved.
        InsufficientFundsError: If the user has insufficient funds to complete the purchase.
    """

    if portfolio_id is None or not ticker or not quantity or quantity <= 0:
        raise TradeExecutionException(
            f"Invalid purchase order parameters [portfolio_id={portfolio_id}, ticker={ticker}, quantity={quantity}]"
        )

    portfolio = db.session.query(Portfolio).filter_by(id=portfolio_id).one_or_none()
    if not portfolio:
        raise TradeExecutionException(f"Portfolio with id {portfolio_id} does not exist.")

    user = portfolio.user
    if not user:
        raise TradeExecutionException(
            f"User associated with the portfolio ({portfolio_id}) does not exist."
        )

    
    quote = get_quote(ticker)
    if quote is None:
        raise TradeExecutionException(f"Unable to resolve ticker {ticker}")

    price = quote.price
    total_cost = price * quantity

    security = db.session.query(Security).filter_by(ticker=ticker).one_or_none()
    if not security:
        security = Security(ticker=ticker, issuer=quote.issuer, price=quote.price)
        db.session.add(security)
    else:
        security.price = quote.price
        
    if user.balance < total_cost:
        raise InsufficientFundsError("Insufficient funds to complete the purchase.")

    
    existing_investment = next(
        (inv for inv in portfolio.investments if inv.ticker == ticker),
        None,
    )

    if existing_investment:
        existing_investment.quantity += quantity
    else:
        portfolio.investments.append(
            Investment(
                ticker=ticker,
                quantity=quantity,
            )
        )

    user.balance -= total_cost

    db.session.add(
        Transaction(
            portfolio_id=portfolio.id,
            username=user.username,
            ticker=ticker,
            quantity=quantity,
            price=price,
            transaction_type="BUY",
            date_time=datetime.datetime.now(),
        )
    )

    db.session.flush()


def liquidate_investment(portfolio_id: int, ticker: str, quantity: int):
    """
    Liquidate shares of a security from a portfolio using the current market price.

    Args:
        portfolio_id (int): The ID of the portfolio to sell from.
        ticker (str): The ticker symbol of the security to sell.
        quantity (int): The number of shares to sell.

    Raises:
        TradeExecutionException: If the parameters, portfolio, investment, or quote are invalid.
    """
    if portfolio_id is None or not ticker or not quantity or quantity <= 0:
        raise TradeExecutionException(
            f"Invalid liquidation parameters [portfolio_id={portfolio_id}, ticker={ticker}, quantity={quantity}]"
        )

    portfolio = db.session.query(Portfolio).filter_by(id=portfolio_id).one_or_none()
    if not portfolio:
        raise TradeExecutionException(f"Portfolio with id {portfolio_id} does not exist")

    user = portfolio.user
    if not user:
        raise TradeExecutionException(
            f"User associated with the portfolio ({portfolio_id}) does not exist."
        )

    quote = get_quote(ticker)
    if quote is None:
        raise TradeExecutionException(f"Could not get current price for {ticker}")

    sale_price = quote.price
    if sale_price is None or sale_price <= 0:
        raise TradeExecutionException(f"Invalid sale price: {sale_price}")

    investment = next(
        (inv for inv in portfolio.investments if inv.ticker == ticker),
        None,
    )

    if not investment:
        raise TradeExecutionException(
            f"No investment with ticker {ticker} exists in portfolio with id {portfolio_id}"
        )

    if investment.quantity < quantity:
        raise TradeExecutionException(
            f"Cannot liquidate {quantity} shares of {ticker}. "
            f"Only {investment.quantity} shares available in portfolio"
        )

    total_proceeds = sale_price * quantity
    user.balance += total_proceeds

    if investment.quantity == quantity:
        db.session.delete(investment)
    else:
        investment.quantity -= quantity

    db.session.add(
        Transaction(
            portfolio_id=portfolio.id,
            username=user.username,
            ticker=ticker,
            quantity=quantity,
            price=sale_price,
            transaction_type="SELL",
            date_time=datetime.datetime.now(),
        )
    )

    db.session.flush()