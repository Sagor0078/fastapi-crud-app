import pytest
from fastapi.testclient import TestClient
from jose import jwt
from datetime import timedelta, datetime
from main import app
from src.routers import auth
import models
import os
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Setup fake environment for testing
os.environ["SECRET_KEY"] = "testsecret"
os.environ["ALGORITHM"] = "HS256"
os.environ["ACCESS_TOKEN_EXPIRE_MINUTES"] = "30"

client = TestClient(app)


class DummyQuery:
    def __init__(self, user):
        self.user = user

    def filter(self, *args, **kwargs):
        return self

    def first(self):
        return self.user


class DummyDB:
    def __init__(self, user):
        self.user = user

    def query(self, model):
        if model == models.User:
            return DummyQuery(self.user)
        raise ValueError("Unsupported model")


@pytest.fixture
def fake_user():
    return models.User(
        username="testuser", hashed_password=pwd_context.hash("secret"), is_active=True
    )


@pytest.fixture
def dummy_db(fake_user):
    return DummyDB(fake_user)


def test_authenticate_user_success(dummy_db, fake_user):
    user = auth.authenticate_user(dummy_db, "testuser", "secret")
    assert user.username == fake_user.username


def test_authenticate_user_failure(dummy_db):
    user = auth.authenticate_user(dummy_db, "testuser", "wrongpassword")
    assert user is False


def create_access_token(data: dict, expires_delta: timedelta):
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode, os.environ["SECRET_KEY"], algorithm=os.environ["ALGORITHM"]
    )
    return encoded_jwt


# def test_login_token_success(monkeypatch, fake_user, dummy_db):
#     def fake_get_db():
#         yield dummy_db

#     # Must patch where get_db is *used* (i.e., src.routers.auth)
#     monkeypatch.setattr("src.routers.auth.get_db", fake_get_db)

#     response = client.post("/api/token", data={"username": "testuser", "password": "secret"})

#     print("Response Code:", response.status_code)
#     print("Response Body:", response.json())

#     assert response.status_code == 200
#     data = response.json()
#     assert "access_token" in data
#     assert data["token_type"] == "bearer"


def test_login_token_failure(monkeypatch, dummy_db):
    def fake_get_db():
        yield dummy_db

    monkeypatch.setattr("src.routers.auth.get_db", fake_get_db)

    response = client.post(
        "/api/token", data={"username": "testuser", "password": "wrongpassword"}
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Incorrect username or password"
