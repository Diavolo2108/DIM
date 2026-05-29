import os
import pytest
from datetime import datetime, timezone
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

os.environ.setdefault("ENCRYPTION_KEY", "Qwk0PQm6j0zLpUI0goHhaaurhc8-b3njkiEYYXI1QBk=")
os.environ.setdefault("ANTHROPIC_API_KEY", "test-key")

from models.base import Base
from models.user import User
from models.client import Client, ClientStatus
from models.post import Post, PostFormat, PostStatus
from services.auth_service import hash_password

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

    # Posts en junio 2026
    for day in [3, 7, 15, 22]:
        _s.add(Post(
            client_id=_client.id,
            scheduled_at=datetime(2026, 6, day, 10, 0, tzinfo=timezone.utc),
            format=PostFormat.IMAGE,
            status=PostStatus.PROGRAMADO,
        ))
    # Post fuera de junio (julio)
    _s.add(Post(
        client_id=_client.id,
        scheduled_at=datetime(2026, 7, 5, 10, 0, tzinfo=timezone.utc),
        format=PostFormat.REEL,
        status=PostStatus.PROGRAMADO,
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


def test_filtrar_posts_por_mes(client):
    res = client.get(f"/posts/?client_id={_client_id}&month=2026-06")
    assert res.status_code == 200
    data = res.json()
    assert len(data) == 4
    for post in data:
        assert post["scheduled_at"].startswith("2026-06")


def test_filtrar_mes_sin_posts(client):
    res = client.get(f"/posts/?client_id={_client_id}&month=2025-01")
    assert res.status_code == 200
    assert res.json() == []


def test_filtrar_julio_devuelve_uno(client):
    res = client.get(f"/posts/?client_id={_client_id}&month=2026-07")
    assert res.status_code == 200
    assert len(res.json()) == 1


def test_formato_month_invalido(client):
    res = client.get(f"/posts/?client_id={_client_id}&month=invalid")
    assert res.status_code == 422


def test_patch_scheduled_at(client):
    # Obtener un post de junio
    posts = client.get(f"/posts/?client_id={_client_id}&month=2026-06").json()
    post_id = posts[0]["id"]
    res = client.patch(f"/posts/{post_id}", json={"scheduled_at": "2026-06-10T18:00:00Z"})
    assert res.status_code == 200
    assert "2026-06-10" in res.json()["scheduled_at"]
