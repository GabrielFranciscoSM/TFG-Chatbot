from datetime import timedelta

import pytest
from jose import jwt

from backend.config import settings
from backend.security import create_access_token, get_password_hash, verify_password


def test_password_hashing():
    password = "secretpassword"
    hashed = get_password_hash(password)
    assert verify_password(password, hashed)
    assert not verify_password("wrongpassword", hashed)


def test_jwt_creation():
    data = {"sub": "testuser", "role": "student"}
    token = create_access_token(data)
    decoded = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    assert decoded["sub"] == "testuser"
    assert decoded["role"] == "student"
    assert "exp" in decoded


def test_jwt_expiration():
    data = {"sub": "testuser"}
    # Create token that expires immediately
    token = create_access_token(data, expires_delta=timedelta(seconds=-1))
    with pytest.raises(jwt.ExpiredSignatureError):
        jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
