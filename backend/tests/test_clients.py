import os
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

# Clave Fernet de test (necesaria antes de importar el módulo)
os.environ.setdefault("ENCRYPTION_KEY", "Qwk0PQm6j0zLpUI0goHhaaurhc8-b3njkiEYYXI1QBk=")

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
    _s.add(User(email="admin@test.com", name="Admin", password_hash=hash_password("test123"), is_active=True))
    _s.commit()


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


# --- Tests de encryption_service ---

def test_encrypt_decrypt_ciclo():
    original = "EAABsbCS...token_de_meta"
    encrypted = encrypt(original)
    assert encrypted != original
    assert decrypt(encrypted) == original


def test_encrypt_produce_valores_distintos():
    token = "mismo_token"
    assert encrypt(token) != encrypt(token)  # Fernet usa IV aleatorio


# --- Tests de API de clientes ---

CLIENTE_PAYLOAD = {
    "name": "Diavolo Lab",
    "instagram_username": "diavolo_lab",
    "instagram_account_id": "17841437345819102",
    "access_token": "EAABsbCS_token_real",
    "status": "EN_PAUSA",
}


def test_crear_cliente(client):
    response = client.post("/clients/", json=CLIENTE_PAYLOAD)
    assert response.status_code == 201
    data = response.json()
    assert data["instagram_username"] == "diavolo_lab"
    assert data["status"] == "EN_PAUSA"
    assert "access_token" not in data  # nunca se devuelve el token


def test_listar_clientes(client):
    response = client.get("/clients/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1


def test_obtener_cliente_por_id(client):
    created = client.post("/clients/", json={**CLIENTE_PAYLOAD, "instagram_username": "diavolo_lab_2"})
    client_id = created.json()["id"]
    response = client.get(f"/clients/{client_id}")
    assert response.status_code == 200
    assert response.json()["id"] == client_id


def test_token_guardado_encriptado(client):
    # Verificar directamente en BD que el token está encriptado
    with Session(_engine) as session:
        db_client = session.query(Client).filter_by(instagram_username="diavolo_lab").first()
        assert db_client is not None
        assert db_client.access_token_encrypted != "EAABsbCS_token_real"
        assert decrypt(db_client.access_token_encrypted) == "EAABsbCS_token_real"


def test_actualizar_estado_cliente(client):
    created = client.post("/clients/", json={**CLIENTE_PAYLOAD, "instagram_username": "lab_update"})
    client_id = created.json()["id"]
    response = client.patch(f"/clients/{client_id}", json={"status": "INACTIVA"})
    assert response.status_code == 200
    assert response.json()["status"] == "INACTIVA"


def test_cliente_no_existente_devuelve_404(client):
    response = client.get("/clients/00000000-0000-0000-0000-000000000000")
    assert response.status_code == 404


def test_username_duplicado_devuelve_409(client):
    client.post("/clients/", json={**CLIENTE_PAYLOAD, "instagram_username": "unique_test"})
    response = client.post("/clients/", json={**CLIENTE_PAYLOAD, "instagram_username": "unique_test"})
    assert response.status_code == 409
