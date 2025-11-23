def test_admin_enroll_success(
    client, professor_token, test_user, mock_users_collection
):
    # Professor enrolling a student
    response = client.post(
        "/admin/enroll",
        json={"username": test_user["username"], "subject": "new_subject"},
        headers={"Authorization": f"Bearer {professor_token}"},
    )
    assert response.status_code == 200
    assert response.json()["status"] == "enrolled"

    # Verify in DB
    updated_user = mock_users_collection.find_one({"username": test_user["username"]})
    assert "new_subject" in updated_user["subjects"]


def test_admin_enroll_forbidden_for_student(client, student_token, test_user):
    # Student trying to enroll themselves (or others)
    response = client.post(
        "/admin/enroll",
        json={"username": test_user["username"], "subject": "hacker_subject"},
        headers={"Authorization": f"Bearer {student_token}"},
    )
    assert response.status_code == 403
    assert "Not authorized" in response.json()["detail"]


def test_admin_unenroll_success(
    client, professor_token, test_user, mock_users_collection
):
    # Ensure user has the subject first
    assert "iv" in test_user["subjects"]

    response = client.post(
        "/admin/unenroll",
        json={"username": test_user["username"], "subject": "iv"},
        headers={"Authorization": f"Bearer {professor_token}"},
    )
    assert response.status_code == 200

    # Verify in DB
    updated_user = mock_users_collection.find_one({"username": test_user["username"]})
    assert "iv" not in updated_user["subjects"]
