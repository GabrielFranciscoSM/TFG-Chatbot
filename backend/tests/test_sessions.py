import uuid
from datetime import UTC, datetime


def test_create_session(client, student_token):
    response = client.post(
        "/sessions",
        json={"title": "My Study Session", "subject": "iv"},
        headers={"Authorization": f"Bearer {student_token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "My Study Session"
    assert data["subject"] == "iv"
    assert "id" in data
    assert "created_at" in data
    assert "last_active" in data


def test_create_session_invalid_subject(client, student_token):
    response = client.post(
        "/sessions",
        json={"title": "Invalid Subject Session", "subject": "math"},
        headers={"Authorization": f"Bearer {student_token}"},
    )
    assert response.status_code == 403
    assert "Not enrolled in this subject" in response.json()["detail"]


def test_get_sessions(client, student_token, mock_sessions_collection, test_user):
    # Create some sessions manually
    session1 = {
        "_id": str(uuid.uuid4()),
        "user_id": test_user["username"],
        "title": "Session 1",
        "subject": "iv",
        "created_at": datetime.now(UTC),
        "last_active": datetime.now(UTC),
    }
    session2 = {
        "_id": str(uuid.uuid4()),
        "user_id": test_user["username"],
        "title": "Session 2",
        "subject": "iv",
        "created_at": datetime.now(UTC),
        "last_active": datetime.now(UTC),
    }
    mock_sessions_collection.insert_many([session1, session2])

    response = client.get(
        "/sessions",
        headers={"Authorization": f"Bearer {student_token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["id"] == session1["_id"]
    assert data[1]["id"] == session2["_id"]


def test_get_session_detail(client, student_token, mock_sessions_collection, test_user):
    session_id = str(uuid.uuid4())
    session = {
        "_id": session_id,
        "user_id": test_user["username"],
        "title": "Detail Session",
        "subject": "iv",
        "created_at": datetime.now(UTC),
        "last_active": datetime.now(UTC),
    }
    mock_sessions_collection.insert_one(session)

    response = client.get(
        f"/sessions/{session_id}",
        headers={"Authorization": f"Bearer {student_token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == session_id
    assert data["title"] == "Detail Session"


def test_get_session_not_found(client, student_token):
    response = client.get(
        "/sessions/nonexistent_id",
        headers={"Authorization": f"Bearer {student_token}"},
    )
    assert response.status_code == 404


def test_get_other_user_session(client, student_token, mock_sessions_collection):
    # Create a session for another user
    session_id = str(uuid.uuid4())
    session = {
        "_id": session_id,
        "user_id": "otheruser",
        "title": "Other User Session",
        "subject": "iv",
        "created_at": datetime.now(UTC),
        "last_active": datetime.now(UTC),
    }
    mock_sessions_collection.insert_one(session)

    response = client.get(
        f"/sessions/{session_id}",
        headers={"Authorization": f"Bearer {student_token}"},
    )
    assert response.status_code == 403


def test_delete_session(client, student_token, mock_sessions_collection, test_user):
    session_id = str(uuid.uuid4())
    session = {
        "_id": session_id,
        "user_id": test_user["username"],
        "title": "Delete Session",
        "subject": "iv",
        "created_at": datetime.now(UTC),
        "last_active": datetime.now(UTC),
    }
    mock_sessions_collection.insert_one(session)

    response = client.delete(
        f"/sessions/{session_id}",
        headers={"Authorization": f"Bearer {student_token}"},
    )
    assert response.status_code == 204

    # Verify deletion
    assert mock_sessions_collection.find_one({"_id": session_id}) is None


def test_delete_other_user_session(client, student_token, mock_sessions_collection):
    session_id = str(uuid.uuid4())
    session = {
        "_id": session_id,
        "user_id": "otheruser",
        "title": "Other User Session",
        "subject": "iv",
        "created_at": datetime.now(UTC),
        "last_active": datetime.now(UTC),
    }
    mock_sessions_collection.insert_one(session)

    response = client.delete(
        f"/sessions/{session_id}",
        headers={"Authorization": f"Bearer {student_token}"},
    )
    assert response.status_code == 403
    assert mock_sessions_collection.find_one({"_id": session_id}) is not None
