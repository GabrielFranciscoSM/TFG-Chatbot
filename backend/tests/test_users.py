def test_read_users_me(client, student_token):
    response = client.get(
        "/users/me", headers={"Authorization": f"Bearer {student_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "student1"
    assert data["role"] == "student"


def test_read_users_me_unauthorized(client):
    response = client.get("/users/me")
    assert response.status_code == 401
