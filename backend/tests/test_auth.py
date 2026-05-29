import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from models.base import Base
from models.user import User
from services.auth_service import hash_password, verify_password, create_access_token, verify_token

TEST_EMAIL = "admin@diavolo.me"
TEST_PASSWORD = "password_test_123"

# Motor SQLite compartido entre threads para los tests de HTTP
_engine = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
Base.metadata.create_all(_engine)

with Session(_engine) as _s:
    _s.add(User(
        email=TEST_EMAIL,
        name="Admin Diavolo",
        password_hash=hash_password(TEST_PASSWORD),
        is_active=True,
    ))
    _s.commit()


def _override_db():
    with Session(_engine) as session:
        yield session


@pytest.fixture(scope="module")
def client():
    from main import app
    from database import get_db
    app.dependency_overrides[get_db] = _override_db
    yield TestClient(app)
    app.dependency_overrides.clear()


def test_hash_y_verify_password():
    hashed = hash_password("mi_password_seguro")
    assert verify_password("mi_password_seguro", hashed)
    assert not verify_password("password_incorrecto", hashed)


def test_create_y_verify_token():
    token = create_access_token({"sub": TEST_EMAIL})
    payload = verify_token(token)
    assert payload["sub"] == TEST_EMAIL


def test_token_expirado_rechazado():
    from datetime import timedelta
    token = create_access_token({"sub": TEST_EMAIL}, expires_delta=timedelta(seconds=-1))
    assert verify_token(token) is None


def test_login_con_credenciales_validas(client):
    response = client.post("/auth/login", json={"email": TEST_EMAIL, "password": TEST_PASSWORD})
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert data["user"]["email"] == TEST_EMAIL


def test_login_con_password_incorrecto(client):
    response = client.post("/auth/login", json={"email": TEST_EMAIL, "password": "wrong"})
    assert response.status_code == 401


def test_login_con_usuario_inexistente(client):
    response = client.post("/auth/login", json={"email": "noexiste@diavolo.me", "password": "x"})
    assert response.status_code == 401


def test_ruta_me_sin_token(client):
    response = client.get("/auth/me")
    assert response.status_code in (401, 403)


def test_ruta_me_con_token_valido(client):
    login = client.post("/auth/login", json={"email": TEST_EMAIL, "password": TEST_PASSWORD})
    token = login.json()["access_token"]
    response = client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert response.json()["email"] == TEST_EMAIL
