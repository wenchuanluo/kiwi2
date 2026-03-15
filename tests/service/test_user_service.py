import pytest

from app.db import db
from app.models.User import User
from app.service import user_service
from app.service.user_service import UnsupportedUserOperationError


def test_create_user_and_get_user(app):
    user_service.create_user(
        username="testuser",
        password="pw",
        firstname="Test",
        lastname="User",
        balance=100.0,
    )
    db.session.commit()

    user = user_service.get_user_by_username("testuser")

    assert user.username == "testuser"
    assert user.balance == 100.0


def test_get_user_with_empty_username():
    with pytest.raises(UnsupportedUserOperationError):
        user_service.get_user_by_username("")


def test_get_all_users(app):
    user_service.create_user(
        username="u1",
        password="pw",
        firstname="A",
        lastname="B",
        balance=10.0,
    )
    db.session.commit()

    users = user_service.get_all_users()

    assert len(users) >= 1


def test_update_user_balance(app):
    user_service.create_user(
        username="balance_user",
        password="pw",
        firstname="A",
        lastname="B",
        balance=50.0,
    )
    db.session.commit()

    user_service.update_user_balance("balance_user", 200.0)
    db.session.commit()

    user = user_service.get_user_by_username("balance_user")

    assert user.balance == 200.0


def test_update_user_balance_user_not_found(app):
    with pytest.raises(UnsupportedUserOperationError):
        user_service.update_user_balance("missing_user", 100)


def test_delete_user_success(app):
    user_service.create_user(
        username="delete_me",
        password="pw",
        firstname="A",
        lastname="B",
        balance=20,
    )
    db.session.commit()

    user_service.delete_user("delete_me")
    db.session.commit()

    user = user_service.get_user_by_username("delete_me")

    assert user is None


def test_delete_admin_user_not_allowed():
    with pytest.raises(UnsupportedUserOperationError):
        user_service.delete_user("admin")


def test_delete_user_not_found(app):
    with pytest.raises(UnsupportedUserOperationError):
        user_service.delete_user("ghost_user")