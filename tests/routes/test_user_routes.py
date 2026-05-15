def mock_auth(monkeypatch, username="admin"):
    class MockValidator:
        def validate_token(self, token):
            return {"username": username}

    monkeypatch.setattr("app.auth._build_validator", lambda: MockValidator())


def auth_headers():
    return {"Authorization": "Bearer fake-token"}


def test_get_users_route(client, monkeypatch):
    mock_auth(monkeypatch)

    response = client.get("/users/", headers=auth_headers())

    assert response.status_code == 200
    assert isinstance(response.json, list)


def test_create_user_route(client, monkeypatch):
    mock_auth(monkeypatch)

    response = client.post(
        "/users/",
        json={
            "username": "route_user",
            "password": "pw",
            "firstname": "Route",
            "lastname": "User",
            "balance": 50.0,
        },
        headers=auth_headers(),
    )

    assert response.status_code == 201
    assert response.json["message"] == "User created successfully"


def test_get_user_route_not_found(client, monkeypatch):
    mock_auth(monkeypatch)

    response = client.get("/users/missing_user", headers=auth_headers())

    assert response.status_code == 404
    assert "not found" in response.json["error"]


def test_update_user_balance_route(client, monkeypatch):
    mock_auth(monkeypatch)

    client.post(
        "/users/",
        json={
            "username": "balance_route_user",
            "password": "pw",
            "firstname": "A",
            "lastname": "B",
            "balance": 10,
        },
        headers=auth_headers(),
    )

    response = client.put(
        "/users/update-balance",
        json={"username": "balance_route_user", "new_balance": 500},
        headers=auth_headers(),
    )

    assert response.status_code == 200
    assert response.json["message"] == "User balance updated successfully"


def test_delete_user_route(client, monkeypatch):
    mock_auth(monkeypatch)

    client.post(
        "/users/",
        json={
            "username": "delete_route_user",
            "password": "pw",
            "firstname": "A",
            "lastname": "B",
            "balance": 10,
        },
        headers=auth_headers(),
    )

    response = client.delete(
        "/users/delete_route_user",
        headers=auth_headers(),
    )

    assert response.status_code == 200
    assert response.json["message"] == "User deleted successfully"