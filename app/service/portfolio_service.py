from typing import List

from app.db import db
from app.models import Portfolio, PortfolioSecurity, User
from app.models.PortfolioSecurity import PortfolioSecurity


class UnsupportedPortfolioOperationError(Exception):
    pass


class PortfolioOperationError(Exception):
    pass


class PortfolioAuthorizationError(Exception):
    pass


def create_portfolio(name: str, description: str, user: User) -> int:
    if not name or not description or not user:
        raise UnsupportedPortfolioOperationError(
            f"Invalid input[name:{name}, description:{description}, user:{user}]. Please try again."
        )

    portfolio = Portfolio(name=name, description=description, user=user)

    db.session.add(portfolio)
    db.session.flush()

    return portfolio.id


def get_portfolios_by_user(user: User) -> List[Portfolio]:
    portfolios = db.session.query(Portfolio).filter_by(owner=user.username).all()
    return portfolios


def get_all_portfolios() -> List[Portfolio]:
    portfolios = db.session.query(Portfolio).all()
    return portfolios


def get_portfolio_by_id(portfolio_id: int) -> Portfolio | None:
    portfolio = db.session.query(Portfolio).filter_by(id=portfolio_id).one_or_none()
    return portfolio


def delete_portfolio(portfolio_id: int):
    portfolio = db.session.query(Portfolio).filter_by(id=portfolio_id).one_or_none()
    if not portfolio:
        raise UnsupportedPortfolioOperationError(f"Portfolio with id {portfolio_id} does not exist")

    db.session.delete(portfolio)
    db.session.flush()



def get_portfolio_access(portfolio_id: int, username: str) -> PortfolioSecurity | None:
    return db.session.query(PortfolioSecurity).filter_by(
        portfolio_id=portfolio_id,
        username=username,
    ).one_or_none()


def grant_portfolio_access(portfolio_id: int, username: str, role: str) -> PortfolioSecurity:
    if role not in {"viewer", "manager"}:
        raise UnsupportedPortfolioOperationError(
            f"Invalid role '{role}'. Role must be 'viewer' or 'manager'."
        )

    portfolio = get_portfolio_by_id(portfolio_id)
    if not portfolio:
        raise UnsupportedPortfolioOperationError(f"Portfolio with id {portfolio_id} does not exist")

    user = db.session.query(User).filter_by(username=username).one_or_none()
    if not user:
        raise UnsupportedPortfolioOperationError(f"User with username {username} does not exist")

    if portfolio.owner == username:
        raise UnsupportedPortfolioOperationError("Cannot grant delegated access to the portfolio owner")

    existing_access = get_portfolio_access(portfolio_id, username)

    if existing_access:
        existing_access.role = role
        db.session.flush()
        return existing_access

    portfolio_access = PortfolioSecurity(
        portfolio_id=portfolio_id,
        username=username,
        role=role,
    )

    db.session.add(portfolio_access)
    db.session.flush()

    return portfolio_access


def revoke_portfolio_access(portfolio_id: int, username: str):
    access = get_portfolio_access(portfolio_id, username)
    if not access:
        raise UnsupportedPortfolioOperationError(
            f"No access grant found for user '{username}' on portfolio {portfolio_id}"
        )

    db.session.delete(access)
    db.session.flush()


def can_view_portfolio(portfolio: Portfolio, username: str) -> bool:
    if portfolio.owner == username:
        return True

    access = get_portfolio_access(portfolio.id, username)
    if not access:
        return False

    return access.role in {"viewer", "manager", "owner"}


def can_manage_portfolio(portfolio: Portfolio, username: str) -> bool:
    if portfolio.owner == username:
        return True

    access = get_portfolio_access(portfolio.id, username)
    if not access:
        return False

    return access.role == "manager"


def ensure_can_view_portfolio(portfolio: Portfolio, username: str):
    if not can_view_portfolio(portfolio, username):
        raise PortfolioAuthorizationError(
            "You do not have permission to view this portfolio."
        )


def ensure_can_manage_portfolio(portfolio: Portfolio, username: str):
    if not can_manage_portfolio(portfolio, username):
        raise PortfolioAuthorizationError(
            "You do not have permission to trade on this portfolio."
        )


def ensure_is_portfolio_owner(portfolio: Portfolio, username: str):
    if portfolio.owner != username:
        raise PortfolioAuthorizationError(
            "Only the portfolio owner can perform this action."
        )