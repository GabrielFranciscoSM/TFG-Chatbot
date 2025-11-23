def test_register_user(client, mock_users_collection):
    response = client.post(
        "/register",
        json={
            "username": "newuser",
            "email": "new@example.com",
            "password": "password123",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "newuser"
    assert data["email"] == "new@example.com"
    assert "password" not in data

    # Verify in DB
    user_in_db = mock_users_collection.find_one({"username": "newuser"})
    assert user_in_db is not None
    assert user_in_db["role"] == "student"  # Default role


def test_register_duplicate_username(client, test_user):
    response = client.post(
        "/register",
        json={
            "username": test_user["username"],
            "email": "other@example.com",
            "password": "password123",
        },
    )
    assert response.status_code == 400
    assert "Username already registered" in response.json()["detail"]


def test_login_success(client, test_user):
    response = client.post(
        "/token",
        data={"username": test_user["username"], "password": "password123"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_wrong_password(client, test_user):
    response = client.post(
        "/token",
        data={"username": test_user["username"], "password": "wrongpassword"},
    )
    assert response.status_code == 401
