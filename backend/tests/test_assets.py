import io
import os
import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

os.environ.setdefault("ENCRYPTION_KEY", "Qwk0PQm6j0zLpUI0goHhaaurhc8-b3njkiEYYXI1QBk=")
os.environ.setdefault("ANTHROPIC_API_KEY", "test-key")
os.environ.setdefault("CLOUDFLARE_R2_BUCKET", "diavolo-test")
os.environ.setdefault("CLOUDFLARE_R2_ENDPOINT", "https://r2.example.com")
os.environ.setdefault("CLOUDFLARE_R2_ACCESS_KEY", "test-key")
os.environ.setdefault("CLOUDFLARE_R2_SECRET_KEY", "test-secret")

from models.base import Base
from models.user import User
from models.client import Client, ClientStatus
from models.asset import Asset
from services.auth_service import hash_password
from services.r2_service import _build_key, _build_public_url

_engine = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
Base.metadata.create_all(_engine)

with Session(_engine) as _s:
    _user = User(email="admin@test.com", name="Admin", password_hash=hash_password("test"), is_active=True)
    _client = Client(
        name="Diavolo Lab", instagram_username="diavolo_lab",
        instagram_account_id="123", access_token_encrypted="tok",
        status=ClientStatus.EN_PAUSA,
    )
    _s.add_all([_user, _client])
    _s.commit()
    _client_id = _client.id


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


# --- Tests de r2_service ---

def test_build_key_contiene_username_y_extension():
    key = _build_key("diavolo_lab", "foto.jpg")
    assert "diavolo_lab" in key
    assert key.endswith(".jpg")  # conserva la extensión
    assert key.count("/") >= 1   # estructura con carpeta


def test_build_public_url_formato_correcto():
    url = _build_public_url("clientes/diavolo_lab/abc123_foto.jpg")
    assert url.startswith("http")
    assert "diavolo_lab" in url


def test_tipo_no_permitido_rechazado(client):
    datos = io.BytesIO(b"fake exe content")
    response = client.post(
        "/assets/upload",
        data={"client_id": _client_id},
        files={"file": ("malware.exe", datos, "application/octet-stream")},
    )
    assert response.status_code == 415


def test_upload_imagen_mock(client):
    imagen_fake = io.BytesIO(b"\xff\xd8\xff" + b"\x00" * 100)  # header JPEG

    mock_r2 = MagicMock()
    with patch("services.r2_service.get_r2_client", return_value=mock_r2):
        response = client.post(
            "/assets/upload",
            data={"client_id": _client_id},
            files={"file": ("foto.jpg", imagen_fake, "image/jpeg")},
        )

    assert response.status_code == 201
    data = response.json()
    assert data["filename"] == "foto.jpg"
    assert data["content_type"] == "image/jpeg"
    assert data["client_id"] == _client_id
    assert "r2_url" in data
    assert "access_token" not in data  # nunca exponer tokens


def test_listar_assets_por_cliente(client):
    response = client.get(f"/assets/?client_id={_client_id}")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert all(a["client_id"] == _client_id for a in data)


def test_eliminar_asset_mock(client):
    # Primero crear un asset en BD directamente
    with Session(_engine) as session:
        asset = Asset(
            client_id=_client_id,
            r2_key="clientes/diavolo_lab/test_delete.jpg",
            r2_url="https://r2.example.com/test_delete.jpg",
            filename="test_delete.jpg",
            content_type="image/jpeg",
            size_bytes=1024,
        )
        session.add(asset)
        session.commit()
        asset_id = asset.id

    mock_r2 = MagicMock()
    with patch("services.r2_service.get_r2_client", return_value=mock_r2):
        response = client.delete(f"/assets/{asset_id}")

    assert response.status_code == 204
    mock_r2.delete_object.assert_called_once()


def test_asset_inexistente_devuelve_404(client):
    response = client.delete("/assets/00000000-0000-0000-0000-000000000000")
    assert response.status_code == 404
