import os
import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

os.environ.setdefault("ENCRYPTION_KEY", "Qwk0PQm6j0zLpUI0goHhaaurhc8-b3njkiEYYXI1QBk=")
os.environ.setdefault("ANTHROPIC_API_KEY", "test-key")

from models.base import Base
from models.user import User
from models.client import Client, ClientStatus
from models.campaign import Campaign, CampaignStatus
from services.auth_service import hash_password
from services.claude_service import build_copy_prompt

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
    _s.flush()
    _campaign = Campaign(
        client_id=_client.id,
        name="Campaña Redes",
        objetivo="Aumentar seguidores",
        frecuencia="3 posts por semana",
        tono="profesional y creativo",
        hashtags=["diseño", "agencia"],
        status=CampaignStatus.ACTIVA,
    )
    _s.add(_campaign)
    _s.commit()
    _client_id = _client.id
    _campaign_id = _campaign.id


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


# --- Tests de build_copy_prompt ---

def test_build_copy_prompt_incluye_contexto():
    prompt = build_copy_prompt(
        campaign_context="Tono profesional. Hashtags: #diseño #agencia",
        instruccion="Post sobre portfolio",
        formato="IMAGE",
    )
    assert "portfolio" in prompt.lower()
    assert "IMAGE" in prompt or "imagen" in prompt.lower()
    assert "diseño" in prompt or "profesional" in prompt.lower()


def test_build_copy_prompt_sin_contexto():
    prompt = build_copy_prompt(
        campaign_context=None,
        instruccion="Post generico",
        formato="REEL",
    )
    assert "Post generico" in prompt


# --- Tests de endpoint POST /posts/ ---

def test_crear_post(client):
    from datetime import datetime, timezone
    response = client.post("/posts/", json={
        "client_id": _client_id,
        "campaign_id": _campaign_id,
        "scheduled_at": "2026-06-01T10:00:00Z",
        "format": "IMAGE",
    })
    assert response.status_code == 201
    data = response.json()
    assert data["status"] == "PROGRAMADO"
    assert data["campaign_id"] == _campaign_id


def test_listar_posts_por_campana(client):
    response = client.get(f"/posts/?campaign_id={_campaign_id}")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_generate_copy_con_mock(client):
    mock_resp = MagicMock()
    mock_resp.content = [MagicMock(text="¡Descubre nuestro portfolio! 🎨\n\n#diseño #agencia #creatividad")]
    with patch("services.claude_service.get_client") as mock_get:
        mock_get.return_value.messages.create.return_value = mock_resp
        response = client.post("/posts/generate-copy", json={
            "campaign_id": _campaign_id,
            "instruccion": "Post sobre nuestro portfolio de proyectos",
            "formato": "IMAGE",
        })
    assert response.status_code == 200
    data = response.json()
    assert "caption" in data
    assert "hashtags" in data
    assert isinstance(data["hashtags"], list)
    assert len(data["caption"]) > 0


def test_generate_copy_campana_inexistente(client):
    response = client.post("/posts/generate-copy", json={
        "campaign_id": "00000000-0000-0000-0000-000000000000",
        "instruccion": "Post",
        "formato": "IMAGE",
    })
    assert response.status_code == 404


def test_actualizar_copy_de_post(client):
    # Crear post
    created = client.post("/posts/", json={
        "client_id": _client_id,
        "campaign_id": _campaign_id,
        "scheduled_at": "2026-06-02T10:00:00Z",
        "format": "CAROUSEL",
    })
    post_id = created.json()["id"]

    # Actualizar copy
    response = client.patch(f"/posts/{post_id}", json={
        "caption": "Caption generado por Claude #instagram",
        "hashtags": ["instagram", "diseño"],
    })
    assert response.status_code == 200
    assert response.json()["caption"] == "Caption generado por Claude #instagram"
