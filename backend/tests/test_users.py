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


def test_get_user_preferences(client, student_token):
    """Test getting user preferences."""
    response = client.get(
        "/users/me/preferences", headers={"Authorization": f"Bearer {student_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    # Default preferences
    assert data["default_test_questions"] == 5
    assert data["default_test_difficulty"] == "medium"


def test_update_user_preferences(client, student_token):
    """Test updating user preferences."""
    new_preferences = {"default_test_questions": 10, "default_test_difficulty": "hard"}

    response = client.put(
        "/users/me/preferences",
        json=new_preferences,
        headers={"Authorization": f"Bearer {student_token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["default_test_questions"] == 10
    assert data["default_test_difficulty"] == "hard"

    # Verify persistence
    response = client.get(
        "/users/me/preferences", headers={"Authorization": f"Bearer {student_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["default_test_questions"] == 10
    assert data["default_test_difficulty"] == "hard"


def test_update_preferences_validation(client, student_token):
    """Test that preferences validation works."""
    # Invalid difficulty
    response = client.put(
        "/users/me/preferences",
        json={"default_test_questions": 5, "default_test_difficulty": "impossible"},
        headers={"Authorization": f"Bearer {student_token}"},
    )
    assert response.status_code == 422  # Validation error

    # Questions out of range
    response = client.put(
        "/users/me/preferences",
        json={"default_test_questions": 100, "default_test_difficulty": "easy"},
        headers={"Authorization": f"Bearer {student_token}"},
    )
    assert response.status_code == 422


def test_get_subject_professor_preferences(client, mock_users_collection):
    """Test getting professor preferences for a subject."""
    # First, add a professor with custom preferences for a subject
    from backend.security import get_password_hash

    mock_users_collection.insert_one(
        {
            "username": "prof_with_prefs",
            "email": "prof_prefs@test.com",
            "hashed_password": get_password_hash("password123"),
            "role": "professor",
            "subjects": ["algebra", "calculus"],
            "preferences": {
                "default_test_questions": 8,
                "default_test_difficulty": "hard",
            },
        }
    )

    # Get preferences for the professor's subject
    response = client.get("/users/subject/algebra/preferences")
    assert response.status_code == 200
    data = response.json()
    assert data["default_test_questions"] == 8
    assert data["default_test_difficulty"] == "hard"


def test_get_subject_professor_preferences_no_professor(client):
    """Test getting preferences for a subject with no professor."""
    # Subject with no professor should return defaults
    response = client.get("/users/subject/nonexistent_subject/preferences")
    assert response.status_code == 200
    data = response.json()
    # Should return default preferences
    assert data["default_test_questions"] == 5
    assert data["default_test_difficulty"] == "medium"


def test_get_subject_professor_preferences_no_custom_prefs(
    client, mock_users_collection
):
    """Test getting preferences for a professor without custom preferences."""
    from backend.security import get_password_hash

    # Professor without preferences field
    mock_users_collection.insert_one(
        {
            "username": "prof_no_prefs",
            "email": "prof_no_prefs@test.com",
            "hashed_password": get_password_hash("password123"),
            "role": "professor",
            "subjects": ["physics"],
        }
    )

    response = client.get("/users/subject/physics/preferences")
    assert response.status_code == 200
    data = response.json()
    # Should return default preferences
    assert data["default_test_questions"] == 5
    assert data["default_test_difficulty"] == "medium"
