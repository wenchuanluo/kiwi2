from app.db import db
from app.models.Portfolio import Portfolio
from app.models.User import User


def mock_auth(monkeypatch, username="admin"):
    class MockValidator:
        def validate_token(self, token):
            return {"username": username}

    monkeypatch.setattr("app.auth._build_validator", lambda: MockValidator())


def auth_headers():
    return {"Authorization": "Bearer fake-token"}


def seed_portfolio(owner_username="owner1"):
    owner = User(
        username=owner_username,
        password="pw",
        firstname="Owner",
        lastname="One",
        balance=1000.0,
    )
    db.session.add(owner)
    db.session.flush()

    portfolio = Portfolio(
        name="Growth",
        description="Growth portfolio",
        user=owner,
    )
    db.session.add(portfolio)
    db.session.commit()

    return owner.username, portfolio.id


def test_get_all_portfolios_route(client, monkeypatch, app):
    mock_auth(monkeypatch)

    with app.app_context():
        seed_portfolio("owner_all")

    response = client.get("/portfolios/", headers=auth_headers())

    assert response.status_code == 200
    assert isinstance(response.json, list)


def test_get_portfolio_route_success(client, monkeypatch, app):
    with app.app_context():
        owner_username, portfolio_id = seed_portfolio("owner_get")

    mock_auth(monkeypatch, owner_username)

    response = client.get(f"/portfolios/{portfolio_id}", headers=auth_headers())

    assert response.status_code == 200
    assert response.json["id"] == portfolio_id


def test_get_portfolio_route_not_found(client, monkeypatch):
    mock_auth(monkeypatch)

    response = client.get("/portfolios/9999", headers=auth_headers())

    assert response.status_code == 404
    assert response.json["error"] == "Portfolio 9999 not found"


def test_get_portfolios_by_user_route_success(client, monkeypatch, app):
    with app.app_context():
        owner_username, portfolio_id = seed_portfolio("owner_by_user")

    mock_auth(monkeypatch)

    response = client.get(f"/portfolios/user/{owner_username}", headers=auth_headers())

    assert response.status_code == 200
    assert isinstance(response.json, list)
    assert len(response.json) >= 1


def test_get_portfolios_by_user_route_user_not_found(client, monkeypatch):
    mock_auth(monkeypatch)

    response = client.get("/portfolios/user/missing_user", headers=auth_headers())

    assert response.status_code == 404
    assert response.json["error"] == "User missing_user not found"


def test_create_portfolio_route_success(client, monkeypatch):
    mock_auth(monkeypatch)

    client.post(
        "/users/",
        json={
            "username": "portfolio_creator",
            "password": "pw",
            "firstname": "Port",
            "lastname": "Creator",
            "balance": 100.0,
        },
        headers=auth_headers(),
    )

    response = client.post(
        "/portfolios/",
        json={
            "username": "portfolio_creator",
            "name": "My Portfolio",
            "description": "Long-term investing",
        },
        headers=auth_headers(),
    )

    assert response.status_code == 201
    assert response.json["message"] == "Portfolio created successfully"
    assert "portfolio_id" in response.json


def test_create_portfolio_route_user_not_found(client, monkeypatch):
    mock_auth(monkeypatch)

    response = client.post(
        "/portfolios/",
        json={
            "username": "no_such_user",
            "name": "My Portfolio",
            "description": "Long-term investing",
        },
        headers=auth_headers(),
    )

    assert response.status_code == 404
    assert response.json["error"] == "User no_such_user not found"


def test_delete_portfolio_route_success(client, monkeypatch, app):
    with app.app_context():
        owner_username, portfolio_id = seed_portfolio("owner_delete")

    mock_auth(monkeypatch, owner_username)

    response = client.delete(f"/portfolios/{portfolio_id}", headers=auth_headers())

    assert response.status_code == 200
    assert response.json["message"] == "Portfolio deleted successfully"


def test_delete_portfolio_route_not_found(client, monkeypatch):
    mock_auth(monkeypatch)

    response = client.delete("/portfolios/9999", headers=auth_headers())

    assert response.status_code == 404
    assert response.json["error"] == "Portfolio 9999 not found"


def test_grant_portfolio_access_route_success(client, monkeypatch, app):
    with app.app_context():
        owner_username, portfolio_id = seed_portfolio("owner_access")
        viewer = User(
            username="viewer_access",
            password="pw",
            firstname="Viewer",
            lastname="User",
            balance=100.0,
        )
        db.session.add(viewer)
        db.session.commit()

    mock_auth(monkeypatch, owner_username)

    response = client.post(
        f"/portfolios/{portfolio_id}/access",
        json={"username": "viewer_access", "role": "viewer"},
        headers=auth_headers(),
    )

    assert response.status_code == 201
    assert response.json["message"] == "Access granted successfully"


def test_revoke_portfolio_access_route_success(client, monkeypatch, app):
    with app.app_context():
        owner_username, portfolio_id = seed_portfolio("owner_revoke")
        viewer = User(
            username="viewer_revoke",
            password="pw",
            firstname="Viewer",
            lastname="User",
            balance=100.0,
        )
        db.session.add(viewer)
        db.session.commit()

        from app.service.portfolio_service import grant_portfolio_access
        grant_portfolio_access(portfolio_id, viewer.username, "viewer")
        db.session.commit()

    mock_auth(monkeypatch, owner_username)

    response = client.delete(
        f"/portfolios/{portfolio_id}/access/viewer_revoke",
        headers=auth_headers(),
    )

    assert response.status_code == 200
    assert response.json["message"] == "Access revoked successfully"