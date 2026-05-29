import os
import pytest
from datetime import datetime, timezone
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

os.environ.setdefault("ENCRYPTION_KEY", "Qwk0PQm6j0zLpUI0goHhaaurhc8-b3njkiEYYXI1QBk=")

from models.base import Base
from models.user import User
from models.client import Client, ClientStatus
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
        access_token_encrypted=encrypt("EAABsbCS_fake"),
        status=ClientStatus.EN_CAMPANA,
    )
    _s.add_all([_user, _client])
    _s.flush()

    # Mensajes de prueba en BD
    for i in range(3):
        _s.add(Message(
            client_id=_client.id,
            instagram_thread_id=f"thread_{i}",
            instagram_message_id=f"msg_{i}",
            sender_id=f"user_{i}",
            sender_username=f"usuario_{i}",
            content=f"Hola, mensaje {i}",
            type=MessageType.DM,
            is_from_page=False,
            replied=False,
        ))
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


# --- Tests del router ---

def test_listar_mensajes(client):
    res = client.get(f"/messages/?client_id={_client_id}")
    assert res.status_code == 200
    data = res.json()
    assert len(data) == 3
    assert all(m["client_id"] == _client_id for m in data)


def test_filtrar_por_tipo_dm(client):
    res = client.get(f"/messages/?client_id={_client_id}&type=DM")
    assert res.status_code == 200
    assert all(m["type"] == "DM" for m in res.json())


def test_listar_no_leidos(client):
    res = client.get(f"/messages/?client_id={_client_id}&replied=false")
    assert res.status_code == 200
    assert all(not m["replied"] for m in res.json())


def test_sync_mensajes_mock(client):
    mock_convs = [
        {
            "id": "thread_nuevo",
            "messages": {"data": [
                {"id": "msg_nuevo_1", "message": "Consulta nueva",
                 "from": {"id": "user_x", "name": "Usuario X"},
                 "created_time": "2026-05-28T10:00:00+0000"},
            ]},
        }
    ]
    with patch("services.inbox_service.get_instagram_conversations", return_value=mock_convs):
        res = client.post(f"/messages/sync?client_id={_client_id}")
    assert res.status_code == 200
    data = res.json()
    assert data["nuevos"] >= 1


def test_responder_mensaje_mock(client):
    # Obtener un mensaje existente
    msgs = client.get(f"/messages/?client_id={_client_id}").json()
    msg_id = msgs[0]["id"]

    def _mock_reply(msg, content, client_obj, db):
        msg.replied = True
        db.commit()
        return "reply_msg_123"

    with patch("routers.messages.send_reply_to_message", side_effect=_mock_reply):
        res = client.post(f"/messages/{msg_id}/reply", json={"content": "Gracias por tu mensaje!"})

    assert res.status_code == 200
    data = res.json()
    assert data["replied"] is True


def test_mensaje_inexistente_devuelve_404(client):
    res = client.post("/messages/00000000-0000-0000-0000-000000000000/reply",
                      json={"content": "test"})
    assert res.status_code == 404
