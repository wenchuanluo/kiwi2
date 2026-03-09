from typing import List

from app.db import db
from app.models import Portfolio, User


class UnsupportedPortfolioOperationError(Exception):
    pass


class PortfolioOperationError(Exception):
    pass


def create_portfolio(name: str, description: str, user: User) -> int:
    if not name or not description or not user:
        raise UnsupportedPortfolioOperationError(
            f"Invalid input[name:{name}, description:{description}, user:{user}]. Please try again."
        )

    portfolio = Portfolio(name=name, description=description, user=user)

    # CHANGED: removed try/except and rollback
    db.session.add(portfolio)

    # CHANGED: kept flush so portfolio.id is available before route-level commit
    db.session.flush()

    return portfolio.id


def get_portfolios_by_user(user: User) -> List[Portfolio]:
    # CHANGED: removed try/except and rollback
    portfolios = db.session.query(Portfolio).filter_by(owner=user.username).all()
    return portfolios


def get_all_portfolios() -> List[Portfolio]:
    # CHANGED: removed try/except and rollback
    portfolios = db.session.query(Portfolio).all()
    return portfolios


def get_portfolio_by_id(portfolio_id: int) -> Portfolio | None:
    # CHANGED: removed try/except and rollback
    portfolio = db.session.query(Portfolio).filter_by(id=portfolio_id).one_or_none()
    return portfolio


def delete_portfolio(portfolio_id: int):
    portfolio = db.session.query(Portfolio).filter_by(id=portfolio_id).one_or_none()
    if not portfolio:
        raise UnsupportedPortfolioOperationError(f"Portfolio with id {portfolio_id} does not exist")

    # CHANGED: removed try/except and rollback
    db.session.delete(portfolio)

    # CHANGED: kept flush for now
    db.session.flush()