import os
import pytest
from datetime import date, datetime, timezone
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

os.environ.setdefault("ENCRYPTION_KEY", "Qwk0PQm6j0zLpUI0goHhaaurhc8-b3njkiEYYXI1QBk=")

from models.base import Base
from models.user import User
from models.client import Client, ClientStatus
from models.metric import Metric
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
    _s.flush()
    # Métricas históricas (últimos 7 días)
    for i in range(7):
        _s.add(Metric(
            client_id=_client.id,
            date=date(2026, 5, 20 + i),
            followers_count=1000 + i * 10,
            reach=500 + i * 50,
            impressions=800 + i * 60,
            engagement_rate=3.5 + i * 0.1,
            profile_views=120 + i * 5,
            website_clicks=30 + i,
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


# --- Tests de endpoint ---

def test_listar_metricas_por_cliente(client):
    res = client.get(f"/metrics/?client_id={_client_id}")
    assert res.status_code == 200
    data = res.json()
    assert len(data) == 7
    assert all(m["client_id"] == _client_id for m in data)


def test_filtrar_metricas_por_rango(client):
    res = client.get(f"/metrics/?client_id={_client_id}&since=2026-05-23&until=2026-05-25")
    assert res.status_code == 200
    data = res.json()
    assert len(data) == 3
    for m in data:
        assert "2026-05-23" <= m["date"] <= "2026-05-25"


def test_listar_metricas_vacio_sin_cliente(client):
    res = client.get("/metrics/?client_id=00000000-0000-0000-0000-000000000000")
    assert res.status_code == 200
    assert res.json() == []


def test_sync_metricas_mock(client):
    mock_profile = MagicMock()
    mock_profile.json.return_value = {"followers_count": 1080, "media_count": 42}
    mock_profile.raise_for_status = MagicMock()

    mock_insights = MagicMock()
    mock_insights.json.return_value = {
        "data": [
            {"name": "impressions", "values": [{"value": 900, "end_time": "2026-05-27T07:00:00+0000"}]},
            {"name": "reach", "values": [{"value": 620, "end_time": "2026-05-27T07:00:00+0000"}]},
            {"name": "profile_views", "values": [{"value": 145, "end_time": "2026-05-27T07:00:00+0000"}]},
            {"name": "website_clicks", "values": [{"value": 38, "end_time": "2026-05-27T07:00:00+0000"}]},
        ]
    }
    mock_insights.raise_for_status = MagicMock()

    with patch("services.meta_service.httpx.get", side_effect=[mock_profile, mock_insights]):
        res = client.post(f"/metrics/sync?client_id={_client_id}")

    assert res.status_code == 200
    data = res.json()
    assert data["followers_count"] == 1080
    assert data["impressions"] == 900


def test_resumen_metricas(client):
    res = client.get(f"/metrics/summary?client_id={_client_id}")
    assert res.status_code == 200
    data = res.json()
    assert "followers_count" in data
    assert "reach_total" in data
    assert "engagement_promedio" in data
