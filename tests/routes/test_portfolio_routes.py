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
    


def _create_user(username):
    user = User(
        username=username,
        password="pw",
        firstname="Test",
        lastname="User",
        balance=100.0,
    )
    db.session.add(user)
    db.session.commit()
    return user


def test_get_portfolio_includes_my_role_as_owner(client, monkeypatch, app):
    with app.app_context():
        owner_username, portfolio_id = seed_portfolio("owner_role_owner")

    mock_auth(monkeypatch, owner_username)

    response = client.get(f"/portfolios/{portfolio_id}", headers=auth_headers())

    assert response.status_code == 200
    assert response.json["my_role"] == "owner"


def test_get_portfolio_includes_my_role_as_viewer(client, monkeypatch, app):
    with app.app_context():
        owner_username, portfolio_id = seed_portfolio("owner_role_viewer")
        _create_user("shared_viewer")

        from app.service.portfolio_service import grant_portfolio_access
        grant_portfolio_access(portfolio_id, "shared_viewer", "viewer")
        db.session.commit()

    mock_auth(monkeypatch, "shared_viewer")

    response = client.get(f"/portfolios/{portfolio_id}", headers=auth_headers())

    assert response.status_code == 200
    assert response.json["my_role"] == "viewer"


def test_get_portfolio_includes_my_role_as_manager(client, monkeypatch, app):
    with app.app_context():
        owner_username, portfolio_id = seed_portfolio("owner_role_manager")
        _create_user("shared_manager")

        from app.service.portfolio_service import grant_portfolio_access
        grant_portfolio_access(portfolio_id, "shared_manager", "manager")
        db.session.commit()

    mock_auth(monkeypatch, "shared_manager")

    response = client.get(f"/portfolios/{portfolio_id}", headers=auth_headers())

    assert response.status_code == 200
    assert response.json["my_role"] == "manager"


def test_get_portfolios_by_user_includes_shared_portfolios(client, monkeypatch, app):
    """
    A user querying their own portfolios list should see both
    portfolios they own AND portfolios shared with them.
    """
    with app.app_context():
        owner_username, portfolio_id = seed_portfolio("owner_share_list")
        _create_user("share_recipient")

        from app.service.portfolio_service import grant_portfolio_access
        grant_portfolio_access(portfolio_id, "share_recipient", "viewer")
        db.session.commit()

    mock_auth(monkeypatch, "share_recipient")

    response = client.get(
        "/portfolios/user/share_recipient", headers=auth_headers()
    )

    assert response.status_code == 200
    assert isinstance(response.json, list)
    assert len(response.json) == 1
    assert response.json[0]["id"] == portfolio_id
    assert response.json[0]["my_role"] == "viewer"


def test_get_portfolios_by_user_includes_both_owned_and_shared(client, monkeypatch, app):
    """
    A user who has their own portfolios AND has been granted access to
    another user's portfolios should see all of them in the listing.
    """
    with app.app_context():
        # User A owns portfolio P1
        owner_a_username, p1_id = seed_portfolio("owner_a_combined")

        # User B owns portfolio P2 (we create directly via service)
        user_b = _create_user("owner_b_combined")
        p2_id = portfolio_service_create_helper(user_b, "B's Portfolio", "B's stuff")

        # User B is granted viewer access on User A's P1
        from app.service.portfolio_service import grant_portfolio_access
        grant_portfolio_access(p1_id, "owner_b_combined", "viewer")
        db.session.commit()

    mock_auth(monkeypatch, "owner_b_combined")

    response = client.get(
        "/portfolios/user/owner_b_combined", headers=auth_headers()
    )

    assert response.status_code == 200
    assert isinstance(response.json, list)
    assert len(response.json) == 2

    portfolio_ids = {p["id"] for p in response.json}
    assert p1_id in portfolio_ids
    assert p2_id in portfolio_ids

    # Check roles are correctly assigned
    role_by_id = {p["id"]: p["my_role"] for p in response.json}
    assert role_by_id[p1_id] == "viewer"   # Shared from A
    assert role_by_id[p2_id] == "owner"    # Owned by B


def portfolio_service_create_helper(user, name, description):
    """Helper to create a portfolio directly via service layer."""
    import app.service.portfolio_service as portfolio_service
    pid = portfolio_service.create_portfolio(
        name=name,
        description=description,
        user=user,
    )
    db.session.commit()
    return pid



def test_delete_portfolio_with_holdings_fails(client, monkeypatch, app):
    """
    Deleting a portfolio that still contains holdings must be rejected
    with a 400 Bad Request.
    """
    from app.models.Investment import Investment

    with app.app_context():
        owner_username, portfolio_id = seed_portfolio("owner_delete_with_holdings")

        # Add an investment (holding) to the portfolio
        investment = Investment(
            portfolio_id=portfolio_id,
            ticker="AAPL",
            quantity=5,
        )
        db.session.add(investment)
        db.session.commit()

    mock_auth(monkeypatch, owner_username)

    response = client.delete(f"/portfolios/{portfolio_id}", headers=auth_headers())

    assert response.status_code == 400
    assert "holdings" in response.json["detail"].lower()