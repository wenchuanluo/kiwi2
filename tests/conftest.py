from __future__ import annotations

import sys
from pathlib import Path
from typing import Generator

import pytest

# Ensure project root is importable
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from app import create_app
from app.config import get_config
from app.db import db

from app.models.User import User
from app.models.Security import Security


@pytest.fixture(scope="function")
def app():
    """
    Create a Flask app configured for testing.
    Uses the TestConfig which runs an in-memory SQLite database.
    """
    config = get_config("test")
    app = create_app(config)

    with app.app_context():
        db.create_all()
        seed_database()

        yield app

        db.session.remove()
        db.drop_all()


@pytest.fixture(scope="function")
def client(app):
    """
    Flask test client for route testing.
    """
    return app.test_client()


@pytest.fixture(scope="function")
def db_session(app) -> Generator:
    """
    Provide the database session for direct database assertions.
    """
    yield db.session


def seed_database():
    """
    Insert baseline data used across tests.
    """
    admin = User(
        username="admin",
        password="password",
        firstname="Admin",
        lastname="User",
        balance=10000.0,
    )

    securities = [
        Security(ticker="AAPL", issuer="Apple Inc.", price=150.0),
        Security(ticker="MSFT", issuer="Microsoft Corp.", price=300.0),
        Security(ticker="GOOGL", issuer="Alphabet Inc.", price=2800.0),
    ]

    db.session.add(admin)
    db.session.add_all(securities)
    db.session.commit()