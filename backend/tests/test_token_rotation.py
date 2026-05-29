import os
import pytest
from datetime import datetime, timezone, timedelta
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

os.environ.setdefault("ENCRYPTION_KEY", "Qwk0PQm6j0zLpUI0goHhaaurhc8-b3njkiEYYXI1QBk=")
os.environ.setdefault("META_APP_ID", "974196185219039")
os.environ.setdefault("META_APP_SECRET", "test_secret")

from models.base import Base
from models.user import User
from models.client import Client, ClientStatus
from services.auth_service import hash_password
from services.encryption_service import encrypt, decrypt

_engine = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
Base.metadata.create_all(_engine)

with Session(_engine) as _s:
    _user = User(email="admin@test.com", name="Admin", password_hash=hash_password("test"), is_active=True)
    # Cliente con token a punto de vencer (en 5 días)
    _client_expiring = Client(
        name="Expiring Client",
        instagram_username="expiring_client",
        instagram_account_id="111",
        access_token_encrypted=encrypt("old_token_expiring"),
        status=ClientStatus.EN_CAMPANA,
        token_expires_at=datetime.now(timezone.utc) + timedelta(days=5),
    )
    # Cliente con token vigente (en 30 días)
    _client_ok = Client(
        name="OK Client",
        instagram_username="ok_client",
        instagram_account_id="222",
        access_token_encrypted=encrypt("ok_token"),
        status=ClientStatus.EN_CAMPANA,
        token_expires_at=datetime.now(timezone.utc) + timedelta(days=30),
    )
    # Cliente sin token_expires_at
    _client_no_expiry = Client(
        name="No Expiry Client",
        instagram_username="no_expiry",
        instagram_account_id="333",
        access_token_encrypted=encrypt("no_expiry_token"),
        status=ClientStatus.EN_PAUSA,
    )
    _s.add_all([_user, _client_expiring, _client_ok, _client_no_expiry])
    _s.commit()
    _expiring_id = _client_expiring.id
    _ok_id = _client_ok.id


def _override_db():
    with Session(_engine) as session:
        yield session


def _override_auth():
    with Session(_engine) as session:
        return session.query(User).filter_by(email="admin@test.com").first()


@pytest.fixture(scope="module")
def client():
    from main import app
    from database import get_db
    from routers.auth import _get_current_user
    app.dependency_overrides[get_db] = _override_db
    app.dependency_overrides[_get_current_user] = _override_auth
    yield TestClient(app)
    app.dependency_overrides.clear()


# --- Tests de meta_service.refresh ---

def test_refresh_token_mock():
    from services.meta_service import refresh_long_lived_token

    mock_resp = MagicMock()
    mock_resp.json.return_value = {"access_token": "new_refreshed_token", "expires_in": 5183944}
    mock_resp.raise_for_status = MagicMock()

    with patch("services.meta_service.httpx.get", return_value=mock_resp):
        new_token, expires_in = refresh_long_lived_token("old_token", "app_id", "app_secret")

    assert new_token == "new_refreshed_token"
    assert expires_in == 5183944


# --- Tests de scheduler de rotación ---

@pytest.mark.asyncio
async def test_rotate_solo_tokens_proximos_a_vencer():
    from services.scheduler import rotate_expiring_tokens

    mock_resp = MagicMock()
    mock_resp.json.return_value = {"access_token": "refreshed_token", "expires_in": 5183944}
    mock_resp.raise_for_status = MagicMock()

    with patch("services.meta_service.httpx.get", return_value=mock_resp):
        await rotate_expiring_tokens(_engine)

    # Solo el cliente con token a 5 días debe haber sido rotado
    with Session(_engine) as session:
        expiring = session.get(Client, _expiring_id)
        ok = session.get(Client, _ok_id)
        assert decrypt(expiring.access_token_encrypted) == "refreshed_token"
        assert decrypt(ok.access_token_encrypted) == "ok_token"  # sin cambio


@pytest.mark.asyncio
async def test_rotate_fallo_no_afecta_otros_clientes():
    from services.scheduler import rotate_expiring_tokens

    with patch("services.meta_service.httpx.get", side_effect=Exception("Meta API error")):
        # No debe lanzar excepción al exterior
        await rotate_expiring_tokens(_engine)


# --- Tests del endpoint de refresh manual ---

def test_refresh_manual_mock(client):
    mock_resp = MagicMock()
    mock_resp.json.return_value = {"access_token": "manually_refreshed", "expires_in": 5183944}
    mock_resp.raise_for_status = MagicMock()

    with patch("services.meta_service.httpx.get", return_value=mock_resp):
        res = client.post(f"/clients/{_expiring_id}/refresh-token")

    assert res.status_code == 200
    data = res.json()
    assert "token_expires_at" in data
    # Verificar que el token fue actualizado en BD
    with Session(_engine) as session:
        c = session.get(Client, _expiring_id)
        assert decrypt(c.access_token_encrypted) == "manually_refreshed"


# --- Test: crear cliente fija token_expires_at ---

def test_crear_cliente_fija_expiry(client):
    res = client.post("/clients/", json={
        "name": "Test Expiry",
        "instagram_username": "test_expiry_new",
        "instagram_account_id": "999",
        "access_token": "brand_new_token",
        "status": "EN_PAUSA",
    })
    assert res.status_code == 201
    data = res.json()
    assert data["token_expires_at"] is not None
