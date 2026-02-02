"""
Tests for the subjects CRUD endpoints.
"""

from datetime import UTC, datetime


def test_create_subject_success(client, admin_token, mock_subjects_collection):
    """Admin can create a new subject."""
    response = client.post(
        "/admin/subjects",
        json={
            "name": "infraestructura-virtual",
            "display_name": "Infraestructura Virtual",
        },
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "infraestructura-virtual"
    assert data["display_name"] == "Infraestructura Virtual"
    assert data["guia_indexed"] is False

    # Verify in DB
    subject = mock_subjects_collection.find_one({"name": "infraestructura-virtual"})
    assert subject is not None
    assert subject["display_name"] == "Infraestructura Virtual"


def test_create_subject_duplicate_fails(client, admin_token, mock_subjects_collection):
    """Creating a duplicate subject fails with 409."""
    # Insert a subject first
    mock_subjects_collection.insert_one(
        {
            "name": "existing-subject",
            "display_name": "Existing Subject",
            "guia_url": None,
            "guia_indexed": False,
            "created_at": datetime.now(UTC),
            "created_by": "admin1",
        }
    )

    response = client.post(
        "/admin/subjects",
        json={"name": "existing-subject", "display_name": "Existing Subject Again"},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.status_code == 409
    assert "already exists" in response.json()["detail"]


def test_create_subject_forbidden_for_professor(client, professor_token):
    """Professors cannot create subjects."""
    response = client.post(
        "/admin/subjects",
        json={"name": "new-subject", "display_name": "New Subject"},
        headers={"Authorization": f"Bearer {professor_token}"},
    )
    assert response.status_code == 403


def test_create_subject_forbidden_for_student(client, student_token):
    """Students cannot create subjects."""
    response = client.post(
        "/admin/subjects",
        json={"name": "new-subject", "display_name": "New Subject"},
        headers={"Authorization": f"Bearer {student_token}"},
    )
    assert response.status_code == 403


def test_list_subjects(
    client, admin_token, mock_subjects_collection, mock_users_collection
):
    """Admin can list all subjects with enrollment counts."""
    # Insert test subjects
    mock_subjects_collection.insert_many(
        [
            {
                "name": "subject-a",
                "display_name": "Subject A",
                "guia_url": None,
                "guia_indexed": False,
                "created_at": datetime.now(UTC),
                "created_by": "admin1",
            },
            {
                "name": "subject-b",
                "display_name": "Subject B",
                "guia_url": "https://example.com",
                "guia_indexed": True,
                "created_at": datetime.now(UTC),
                "created_by": "admin1",
            },
        ]
    )

    response = client.get(
        "/admin/subjects",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 2
    assert len(data["subjects"]) == 2


def test_list_subjects_public_no_auth(client, mock_subjects_collection):
    """Public endpoint returns subjects without authentication."""
    # Insert test subjects
    mock_subjects_collection.insert_many(
        [
            {
                "name": "subject-a",
                "display_name": "Subject A",
                "guia_url": None,
                "guia_indexed": False,
                "created_at": datetime.now(UTC),
                "created_by": "admin1",
            },
            {
                "name": "subject-b",
                "display_name": "Subject B",
                "guia_url": "https://example.com",
                "guia_indexed": True,
                "created_at": datetime.now(UTC),
                "created_by": "admin1",
            },
        ]
    )

    response = client.get("/subjects")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    # Public endpoint returns minimal info
    assert all("name" in s and "display_name" in s for s in data)
    # Should not include sensitive info
    assert all("created_by" not in s for s in data)


def test_delete_subject_success(client, admin_token, mock_subjects_collection):
    """Admin can delete an empty subject."""
    mock_subjects_collection.insert_one(
        {
            "name": "to-delete",
            "display_name": "To Delete",
            "guia_url": None,
            "guia_indexed": False,
            "created_at": datetime.now(UTC),
            "created_by": "admin1",
        }
    )

    response = client.delete(
        "/admin/subjects/to-delete",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.status_code == 200
    assert response.json()["status"] == "deleted"

    # Verify deleted
    assert mock_subjects_collection.find_one({"name": "to-delete"}) is None


def test_delete_subject_with_enrolled_users_requires_force(
    client, admin_token, mock_subjects_collection, mock_users_collection
):
    """Cannot delete subject with enrolled users unless force=true."""
    mock_subjects_collection.insert_one(
        {
            "name": "enrolled-subject",
            "display_name": "Enrolled Subject",
            "guia_url": None,
            "guia_indexed": False,
            "created_at": datetime.now(UTC),
            "created_by": "admin1",
        }
    )
    mock_users_collection.insert_one(
        {
            "username": "enrolled_student",
            "subjects": ["enrolled-subject"],
            "role": "student",
        }
    )

    # Without force - should fail
    response = client.delete(
        "/admin/subjects/enrolled-subject",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.status_code == 409
    assert "enrolled users" in response.json()["detail"]

    # With force - should succeed
    response = client.delete(
        "/admin/subjects/enrolled-subject?force=true",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.status_code == 200
    assert response.json()["users_affected"] == 1

    # Verify subject removed from user
    user = mock_users_collection.find_one({"username": "enrolled_student"})
    assert "enrolled-subject" not in user["subjects"]


def test_delete_subject_not_found(client, admin_token):
    """Deleting non-existent subject returns 404."""
    response = client.delete(
        "/admin/subjects/nonexistent",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.status_code == 404


def test_assign_subject_validates_existence(
    client, admin_token, test_professor, mock_subjects_collection
):
    """Assigning a non-existent subject returns 404."""
    response = client.post(
        "/admin/assign-subject",
        json={"username": test_professor["username"], "subject": "nonexistent"},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.status_code == 404
    assert "Subject not found" in response.json()["detail"]

    # Create the subject first
    mock_subjects_collection.insert_one(
        {
            "name": "new-subject",
            "display_name": "New Subject",
            "guia_url": None,
            "guia_indexed": False,
            "created_at": datetime.now(UTC),
            "created_by": "admin1",
        }
    )

    # Now assignment should work
    response = client.post(
        "/admin/assign-subject",
        json={"username": test_professor["username"], "subject": "new-subject"},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.status_code == 200


def test_enroll_validates_subject_existence(
    client, professor_token, test_user, mock_subjects_collection
):
    """Enrolling in a non-existent subject returns 404."""
    response = client.post(
        "/admin/enroll",
        json={"username": test_user["username"], "subject": "nonexistent"},
        headers={"Authorization": f"Bearer {professor_token}"},
    )
    assert response.status_code == 404
    assert "Subject not found" in response.json()["detail"]


def test_batch_enroll_success(
    client, admin_token, mock_subjects_collection, mock_users_collection
):
    """Admin can batch enroll multiple students."""
    # Create subject
    mock_subjects_collection.insert_one(
        {
            "name": "batch-subject",
            "display_name": "Batch Subject",
            "guia_url": None,
            "guia_indexed": False,
            "created_at": datetime.now(UTC),
            "created_by": "admin1",
        }
    )

    # Create students
    mock_users_collection.insert_many(
        [
            {
                "username": "student_batch_1",
                "email": "s1@example.com",
                "role": "student",
                "subjects": [],
            },
            {
                "username": "student_batch_2",
                "email": "s2@example.com",
                "role": "student",
                "subjects": [],
            },
        ]
    )

    response = client.post(
        "/admin/enroll-batch",
        json={
            "usernames": ["student_batch_1", "student_batch_2", "nonexistent_user"],
            "subject": "batch-subject",
        },
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["enrolled_count"] == 2
    assert "student_batch_1" in data["enrolled"]
    assert "student_batch_2" in data["enrolled"]
    assert "nonexistent_user" in data["not_found"]

    # Verify in DB
    s1 = mock_users_collection.find_one({"username": "student_batch_1"})
    assert "batch-subject" in s1["subjects"]
