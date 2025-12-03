def test_admin_enroll_success(
    client, professor_token, test_user, mock_users_collection
):
    # Professor enrolling a student in their own subject (dsd)
    response = client.post(
        "/admin/enroll",
        json={"username": test_user["username"], "subject": "dsd"},
        headers={"Authorization": f"Bearer {professor_token}"},
    )
    assert response.status_code == 200
    assert response.json()["status"] == "enrolled"

    # Verify in DB
    updated_user = mock_users_collection.find_one({"username": test_user["username"]})
    assert "dsd" in updated_user["subjects"]


def test_admin_enroll_forbidden_for_student(client, student_token, test_user):
    # Student trying to enroll themselves (or others)
    response = client.post(
        "/admin/enroll",
        json={"username": test_user["username"], "subject": "hacker_subject"},
        headers={"Authorization": f"Bearer {student_token}"},
    )
    assert response.status_code == 403
    assert "Not authorized" in response.json()["detail"]


def test_admin_enroll_forbidden_for_professor_wrong_subject(
    client, professor_token, test_user
):
    # Professor trying to enroll in a subject they don't manage
    response = client.post(
        "/admin/enroll",
        json={"username": test_user["username"], "subject": "other_subject"},
        headers={"Authorization": f"Bearer {professor_token}"},
    )
    assert response.status_code == 403
    assert "only enroll students in your own subjects" in response.json()["detail"]


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


# ===================== Admin-only endpoints =====================


def test_admin_get_stats(client, admin_token, test_user, test_professor, test_admin):
    """Admin can get system stats"""
    response = client.get(
        "/admin/stats",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "total_students" in data
    assert "total_professors" in data
    assert "total_admins" in data
    assert data["total_students"] == 1  # test_user
    assert data["total_professors"] == 1  # test_professor
    assert data["total_admins"] == 1  # test_admin


def test_admin_get_stats_forbidden_for_professor(client, professor_token):
    """Professors cannot access admin stats"""
    response = client.get(
        "/admin/stats",
        headers={"Authorization": f"Bearer {professor_token}"},
    )
    assert response.status_code == 403


def test_admin_get_users(client, admin_token, test_user, test_professor, test_admin):
    """Admin can list all users"""
    response = client.get(
        "/admin/users",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 3  # student, professor, admin
    usernames = [u["username"] for u in data]
    assert "student1" in usernames
    assert "prof1" in usernames
    assert "admin1" in usernames


def test_admin_get_users_filter_by_role(
    client, admin_token, test_user, test_professor, test_admin
):
    """Admin can filter users by role"""
    response = client.get(
        "/admin/users?role=professor",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["username"] == "prof1"


def test_admin_assign_subject(
    client, admin_token, test_professor, mock_users_collection
):
    """Admin can assign a subject to a professor"""
    response = client.post(
        "/admin/assign-subject",
        json={"username": test_professor["username"], "subject": "new_subject"},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.status_code == 200

    # Verify in DB
    updated = mock_users_collection.find_one({"username": test_professor["username"]})
    assert "new_subject" in updated["subjects"]


def test_admin_assign_subject_forbidden_for_professor(
    client, professor_token, test_professor
):
    """Professors cannot assign subjects to themselves"""
    response = client.post(
        "/admin/assign-subject",
        json={"username": test_professor["username"], "subject": "new_subject"},
        headers={"Authorization": f"Bearer {professor_token}"},
    )
    assert response.status_code == 403


def test_admin_promote_user(client, admin_token, test_user, mock_users_collection):
    """Admin can promote a student to professor"""
    response = client.post(
        "/admin/promote",
        json={"username": test_user["username"], "new_role": "professor"},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.status_code == 200

    # Verify in DB
    updated = mock_users_collection.find_one({"username": test_user["username"]})
    assert updated["role"] == "professor"


def test_admin_promote_forbidden_for_professor(client, professor_token, test_user):
    """Professors cannot promote users"""
    response = client.post(
        "/admin/promote",
        json={"username": test_user["username"], "new_role": "professor"},
        headers={"Authorization": f"Bearer {professor_token}"},
    )
    assert response.status_code == 403
