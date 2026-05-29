import os
import pytest
from pathlib import Path
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
from services.campaign_service import (
    _generar_contexto_md,
    _generar_aprobacion_md,
    crear_estructura_carpeta,
)

_engine = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
Base.metadata.create_all(_engine)

with Session(_engine) as _s:
    _user = User(email="admin@test.com", name="Admin", password_hash=hash_password("test"), is_active=True)
    _client = Client(
        name="Diavolo Lab",
        instagram_username="diavolo_lab",
        instagram_account_id="123",
        access_token_encrypted="tok",
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


HISTORIAL_PRUEBA = [
    {"role": "user", "content": "Quiero aumentar seguidores para una agencia de diseño"},
    {"role": "assistant", "content": "Propongo una campaña de 4 semanas con 3 posts semanales en tono profesional."},
]

DATOS_PRUEBA = {
    "objetivo": "Aumentar seguidores en 500",
    "duracion_semanas": 4,
    "frecuencia": "3 posts por semana",
    "tono": "profesional y creativo",
    "hashtags": ["diseño", "agencia", "creatividad"],
    "horarios_sugeridos": "Martes y jueves 18:00, sábados 11:00",
    "posts_propuestos": [
        {"semana": 1, "formato": "IMAGE", "tema": "Presentación de la agencia"},
        {"semana": 2, "formato": "CAROUSEL", "tema": "Portfolio de proyectos"},
    ],
}


# --- Tests de generación de documentos ---

def test_generar_contexto_md_contiene_campos():
    contenido = _generar_contexto_md("Campaña de prueba", DATOS_PRUEBA)
    assert "Campaña de prueba" in contenido
    assert "Aumentar seguidores" in contenido
    assert "3 posts por semana" in contenido
    assert "profesional" in contenido
    assert "#diseño" in contenido


def test_generar_aprobacion_md_contiene_campos():
    contenido = _generar_aprobacion_md("diavolo_lab", "Campaña de prueba", DATOS_PRUEBA)
    assert "diavolo_lab" in contenido
    assert "Aumentar seguidores" in contenido
    assert "Calendario de publicaciones" in contenido


def test_crear_estructura_carpeta(tmp_path):
    with patch("services.campaign_service.CLIENTES_BASE", tmp_path):
        carpeta = crear_estructura_carpeta("diavolo_lab", "Mi Campaña Test")
        assert carpeta.exists()
        assert (carpeta / "assets").exists()
        assert "@diavolo_lab" in str(carpeta)
        assert "mi-campana-test" in str(carpeta).lower()


# --- Tests de endpoint POST /campaigns ---

def test_crear_campana_guarda_en_bd(client, tmp_path):
    mock_datos = MagicMock(return_value=DATOS_PRUEBA)
    mock_claude = MagicMock()
    mock_claude.content = [MagicMock(text='{"objetivo":"Aumentar seguidores","duracion_semanas":4,"frecuencia":"3 posts por semana","tono":"profesional","hashtags":["diseño"],"horarios_sugeridos":"18:00","posts_propuestos":[]}')]
    mock_get = MagicMock(return_value=MagicMock(messages=MagicMock(create=MagicMock(return_value=mock_claude))))

    with patch("services.campaign_service.CLIENTES_BASE", tmp_path), \
         patch("services.campaign_service.get_client", mock_get):
        response = client.post("/campaigns/", json={
            "client_id": _client_id,
            "name": "Campaña Test",
            "objetivo": "Aumentar seguidores",
            "historial": HISTORIAL_PRUEBA,
        })

    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Campaña Test"
    assert data["status"] == "PLANIFICACION"
    assert data["contexto_path"] is not None
    assert data["aprobacion_path"] is not None


def test_listar_campanas(client, tmp_path):
    response = client.get("/campaigns/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert len(response.json()) >= 1


def test_listar_campanas_por_cliente(client):
    response = client.get(f"/campaigns/?client_id={_client_id}")
    assert response.status_code == 200
    for c in response.json():
        assert c["client_id"] == _client_id


def test_obtener_campana_por_id(client, tmp_path):
    mock_claude = MagicMock()
    mock_claude.content = [MagicMock(text='{"objetivo":"Test","duracion_semanas":2,"frecuencia":"2 por semana","tono":"casual","hashtags":[],"horarios_sugeridos":"—","posts_propuestos":[]}')]
    mock_get = MagicMock(return_value=MagicMock(messages=MagicMock(create=MagicMock(return_value=mock_claude))))

    with patch("services.campaign_service.CLIENTES_BASE", tmp_path), \
         patch("services.campaign_service.get_client", mock_get):
        created = client.post("/campaigns/", json={
            "client_id": _client_id,
            "name": "Campaña Para ID Test",
            "objetivo": "Test",
            "historial": HISTORIAL_PRUEBA,
        })
    campaign_id = created.json()["id"]
    response = client.get(f"/campaigns/{campaign_id}")
    assert response.status_code == 200
    assert response.json()["id"] == campaign_id


def test_campana_cliente_inexistente_devuelve_404(client):
    response = client.post("/campaigns/", json={
        "client_id": "00000000-0000-0000-0000-000000000000",
        "name": "Sin cliente",
        "objetivo": "Test",
        "historial": [],
    })
    assert response.status_code == 404
