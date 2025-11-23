import os

import mongomock
import pytest
from fastapi.testclient import TestClient

# Set env vars BEFORE importing app
os.environ["SECRET_KEY"] = "testsecret"
os.environ["ALGORITHM"] = "HS256"
os.environ["MONGO_DB"] = "test_db"

from backend.api import app
from backend.dependencies import get_users_collection
from backend.models import UserRole
from backend.security import create_access_token, get_password_hash


@pytest.fixture
def mock_mongo_client():
    return mongomock.MongoClient()


@pytest.fixture
def mock_users_collection(mock_mongo_client):
    db = mock_mongo_client.test_db
    return db.users


@pytest.fixture
def client(mock_users_collection):
    # Override the dependency to use mongomock
    def override_get_users_collection():
        return mock_users_collection

    app.dependency_overrides[get_users_collection] = override_get_users_collection
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture
def test_user(mock_users_collection):
    user_data = {
        "username": "student1",
        "email": "student1@example.com",
        "hashed_password": get_password_hash("password123"),
        "role": UserRole.STUDENT,
        "subjects": ["iv"],
    }
    mock_users_collection.insert_one(user_data)
    return user_data


@pytest.fixture
def test_professor(mock_users_collection):
    user_data = {
        "username": "prof1",
        "email": "prof1@example.com",
        "hashed_password": get_password_hash("password123"),
        "role": UserRole.PROFESSOR,
        "subjects": [],
    }
    mock_users_collection.insert_one(user_data)
    return user_data


@pytest.fixture
def student_token(test_user):
    return create_access_token(
        data={
            "sub": test_user["username"],
            "role": test_user["role"],
            "subjects": test_user["subjects"],
        }
    )


@pytest.fixture
def professor_token(test_professor):
    return create_access_token(
        data={
            "sub": test_professor["username"],
            "role": test_professor["role"],
            "subjects": test_professor["subjects"],
        }
    )
