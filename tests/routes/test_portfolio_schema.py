import pytest
from pydantic import ValidationError

from app.routes.domain.portfolio_schema import CreatePortfolioRequest


def test_create_portfolio_request_valid():
    request = CreatePortfolioRequest(
        username="serena",
        name="Growth Portfolio",
        description="Long-term equity holdings",
    )

    assert request.username == "serena"
    assert request.name == "Growth Portfolio"
    assert request.description == "Long-term equity holdings"


def test_create_portfolio_request_missing_username_raises_validation_error():
    with pytest.raises(ValidationError):
        CreatePortfolioRequest(
            name="Growth Portfolio",
            description="Long-term equity holdings",
        )


def test_create_portfolio_request_empty_name_raises_validation_error():
    with pytest.raises(ValidationError):
        CreatePortfolioRequest(
            username="serena",
            name="",
            description="Long-term equity holdings",
        )


def test_create_portfolio_request_empty_description_raises_validation_error():
    with pytest.raises(ValidationError):
        CreatePortfolioRequest(
            username="serena",
            name="Growth Portfolio",
            description="",
        )