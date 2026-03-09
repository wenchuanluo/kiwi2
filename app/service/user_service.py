from typing import List

from sqlalchemy.exc import IntegrityError

from app.db import db
from app.models.User import User


class UnsupportedUserOperationError(Exception):
    pass


def get_user_by_username(username: str) -> User | None:
    if not username:
        raise UnsupportedUserOperationError("Username cannot be empty")

    # CHANGED: removed try/except and rollback
    return db.session.query(User).filter_by(username=username).one_or_none()


def get_all_users() -> List[User]:
    # CHANGED: removed try/except and rollback
    users = db.session.query(User).all()
    return users


def update_user_balance(username: str, new_balance: float):
    # CHANGED: removed try/except and rollback
    user = db.session.query(User).filter_by(username=username).one_or_none()
    if not user:
        raise UnsupportedUserOperationError(f"User with username {username} does not exist")

    user.balance = new_balance

    # CHANGED: kept flush for now
    db.session.flush()


def create_user(username: str, password: str, firstname: str, lastname: str, balance: float):
    # CHANGED: removed try/except and rollback
    db.session.add(
        User(
            username=username,
            password=password,
            firstname=firstname,
            lastname=lastname,
            balance=balance,
        )
    )

    # CHANGED: kept flush for now
    db.session.flush()


def delete_user(username: str):
    if username == "admin":
        raise UnsupportedUserOperationError("Cannot delete admin user")
    if not username:
        raise UnsupportedUserOperationError("Username cannot be empty")

    user = db.session.query(User).filter_by(username=username).one_or_none()
    if not user:
        raise UnsupportedUserOperationError(f"User with username {username} does not exist")

    try:
        db.session.delete(user)
        db.session.flush()

    # CHANGED: kept specific business exception mapping for dependency constraint
    except IntegrityError:
        raise UnsupportedUserOperationError(
            f"Cannot delete user {username} due to existing dependencies"
        )