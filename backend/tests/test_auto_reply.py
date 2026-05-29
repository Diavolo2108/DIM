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
from models.auto_reply import AutoReply
from models.message import Message, MessageType
from services.auth_service import hash_password
from services.encryption_service import encrypt

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
        instagram_account_id="17841437345819102",
        access_token_encrypted=encrypt("fake_token"),
        status=ClientStatus.EN_CAMPANA,
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


# --- CRUD de auto_reply ---

def test_crear_auto_reply(client):
    res = client.put(f"/auto-replies/{_client_id}", json={
        "is_active": False,
        "system_prompt": "Eres el asistente de Diavolo Lab. Responde de forma profesional.",
        "delay_seconds": 0,
    })
    assert res.status_code == 200
    data = res.json()
    assert data["client_id"] == _client_id
    assert data["is_active"] is False


def test_obtener_auto_reply(client):
    res = client.get(f"/auto-replies/{_client_id}")
    assert res.status_code == 200
    assert res.json()["client_id"] == _client_id


def test_activar_auto_reply(client):
    res = client.patch(f"/auto-replies/{_client_id}/toggle")
    assert res.status_code == 200
    assert res.json()["is_active"] is True


def test_desactivar_auto_reply(client):
    res = client.patch(f"/auto-replies/{_client_id}/toggle")
    assert res.status_code == 200
    assert res.json()["is_active"] is False


def test_auto_reply_inexistente_devuelve_404(client):
    res = client.get("/auto-replies/00000000-0000-0000-0000-000000000000")
    assert res.status_code == 404


# --- Lógica de autorrespuesta ---

def test_generar_autorrespuesta_con_mock():
    from services.inbox_service import _generar_autorrespuesta
    mock_resp = MagicMock()
    mock_resp.content = [MagicMock(text="Hola! Gracias por tu mensaje. Te responderemos pronto.")]

    with patch("services.inbox_service.get_client") as mock_get:
        mock_get.return_value.messages.create.return_value = mock_resp
        result = _generar_autorrespuesta(
            system_prompt="Eres el asistente de Diavolo Lab.",
            message_content="Hola, quiero saber el precio de sus servicios",
        )
    assert "gracias" in result.lower() or len(result) > 0


def test_sync_con_autorrespuesta_activa():
    from services.inbox_service import sync_client_messages

    mock_convs = [{
        "id": "thread_ar",
        "messages": {"data": [{
            "id": "msg_ar_001",
            "message": "Hola, me interesa contratar sus servicios",
            "from": {"id": "user_ar", "name": "Cliente AR"},
            "created_time": "2026-05-28T10:00:00+0000",
        }]},
    }]

    mock_claude = MagicMock()
    mock_claude.content = [MagicMock(text="Gracias por tu mensaje! Te contactamos pronto.")]

    with Session(_engine) as session:
        # Activar la autorrespuesta ya creada
        ar = session.query(AutoReply).filter_by(client_id=_client_id).first()
        if ar:
            ar.is_active = True
            ar.system_prompt = "Eres asistente de Diavolo."
        else:
            ar = AutoReply(client_id=_client_id, is_active=True,
                           system_prompt="Eres asistente de Diavolo.")
            session.add(ar)
        session.commit()

        client_obj = session.get(Client, _client_id)

        with patch("services.inbox_service.get_instagram_conversations", return_value=mock_convs), \
             patch("services.inbox_service.send_dm_reply", return_value="reply_auto_001"), \
             patch("services.inbox_service.get_client") as mock_get:
            mock_get.return_value.messages.create.return_value = mock_claude
            nuevos = sync_client_messages(client_obj, session)

        # Verificar que el DM fue respondido
        msg = session.query(Message).filter_by(instagram_message_id="msg_ar_001").first()
        assert msg is not None
        assert msg.replied is True
