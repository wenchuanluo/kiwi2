import pytest
from pydantic import ValidationError

from app.routes.domain.user_schema import CreateUserRequest, UpdateUserBalanceRequest

def test_create_user_request_valid():
    request = CreateUserRequest(
        username="serena",
        password="secret123",
        firstname="Serena",
        lastname="Luo",
        balance=1000.0,
    )

    assert request.username == "serena"
    assert request.password == "secret123"
    assert request.firstname == "Serena"
    assert request.lastname == "Luo"
    assert request.balance == 1000.0


def test_create_user_request_missing_username_raises_validation_error():
    with pytest.raises(ValidationError):
        CreateUserRequest(
            password="secret123",
            firstname="Serena",
            lastname="Luo",
            balance=1000.0,
        )


def test_create_user_request_empty_password_raises_validation_error():
    with pytest.raises(ValidationError):
        CreateUserRequest(
            username="serena",
            password="",
            firstname="Serena",
            lastname="Luo",
            balance=1000.0,
        )


def test_create_user_request_negative_balance_raises_validation_error():
    with pytest.raises(ValidationError):
        CreateUserRequest(
            username="serena",
            password="secret123",
            firstname="Serena",
            lastname="Luo",
            balance=-1.0,
        )


def test_update_user_balance_request_valid():
    request = UpdateUserBalanceRequest(
        username="serena",
        new_balance=2500.0,
    )

    assert request.username == "serena"
    assert request.new_balance == 2500.0


def test_update_user_balance_request_empty_username_raises_validation_error():
    with pytest.raises(ValidationError):
        UpdateUserBalanceRequest(
            username="",
            new_balance=2500.0,
        )


def test_update_user_balance_request_negative_balance_raises_validation_error():
    with pytest.raises(ValidationError):
        UpdateUserBalanceRequest(
            username="serena",
            new_balance=-100.0,
        )