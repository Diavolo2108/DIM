import os
import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

os.environ.setdefault("ENCRYPTION_KEY", "Qwk0PQm6j0zLpUI0goHhaaurhc8-b3njkiEYYXI1QBk=")
os.environ.setdefault("ANTHROPIC_API_KEY", "test-key")

from models.base import Base
from models.user import User
from services.auth_service import hash_password
from services.claude_service import build_planning_messages, PLANNING_SYSTEM_PROMPT

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


# --- Tests de claude_service ---

def test_planning_system_prompt_existe():
    assert len(PLANNING_SYSTEM_PROMPT) > 100
    assert "campaña" in PLANNING_SYSTEM_PROMPT.lower() or "instagram" in PLANNING_SYSTEM_PROMPT.lower()


def test_build_planning_messages_formato():
    messages = build_planning_messages(
        historial=[{"role": "user", "content": "Quiero aumentar seguidores"}],
        contexto_cliente="@diavolo_lab — agencia de diseño",
    )
    assert isinstance(messages, list)
    assert messages[0]["role"] == "user"
    assert all("role" in m and "content" in m for m in messages)


def test_build_planning_messages_incluye_contexto():
    contexto = "Cliente: Nike — ropa deportiva"
    messages = build_planning_messages(
        historial=[{"role": "user", "content": "Hola"}],
        contexto_cliente=contexto,
    )
    # El contexto del cliente debe aparecer en algún mensaje
    contenido_total = " ".join(m["content"] for m in messages)
    assert contexto in contenido_total


# --- Tests del endpoint de planificación ---

def test_plan_endpoint_requiere_auth():
    from main import app
    from database import get_db
    from routers.auth import _get_current_user
    # Sin overrides — sin auth
    app.dependency_overrides.clear()
    c = TestClient(app)
    res = c.post("/campaigns/plan", json={"message": "hola", "historial": []})
    assert res.status_code in (401, 403)
    # Restaurar
    app.dependency_overrides[get_db] = _override_db
    app.dependency_overrides[_get_current_user] = _override_auth


def test_plan_endpoint_con_mock_claude(client):
    mock_response = MagicMock()
    mock_response.content = [MagicMock(text="Te propongo una campaña de 4 semanas con 3 posts semanales.")]

    with patch("services.claude_service.get_client") as mock_get:
        mock_client = MagicMock()
        mock_client.messages.create.return_value = mock_response
        mock_get.return_value = mock_client

        res = client.post("/campaigns/plan", json={
            "message": "Quiero aumentar seguidores para una agencia de diseño",
            "historial": [],
            "contexto_cliente": "@diavolo_lab",
        })

    assert res.status_code == 200
    data = res.json()
    assert "respuesta" in data
    assert len(data["respuesta"]) > 0
