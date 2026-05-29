import os
import pytest
from datetime import date
from unittest.mock import patch, MagicMock
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

os.environ.setdefault("ENCRYPTION_KEY", "Qwk0PQm6j0zLpUI0goHhaaurhc8-b3njkiEYYXI1QBk=")
os.environ.setdefault("RESEND_API_KEY", "re_test_key")
os.environ.setdefault("RESEND_FROM", "reportes@diavolo.agency")
os.environ.setdefault("REPORT_EMAIL", "equipo@diavolo.agency")

from models.base import Base
from models.client import Client, ClientStatus
from models.metric import Metric
from models.post import Post, PostFormat, PostStatus
from services.encryption_service import encrypt

_engine = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
Base.metadata.create_all(_engine)

with Session(_engine) as _s:
    _client = Client(
        name="Diavolo Lab", instagram_username="diavolo_lab",
        instagram_account_id="17841437345819102",
        access_token_encrypted=encrypt("fake_token"),
        status=ClientStatus.EN_CAMPANA,
    )
    _s.add(_client)
    _s.flush()

    for i in range(7):
        _s.add(Metric(
            client_id=_client.id, date=date(2026, 5, 21 + i),
            followers_count=1000 + i * 10, reach=500 + i * 50,
            impressions=800 + i * 60, engagement_rate=3.5 + i * 0.1,
            profile_views=120 + i * 5, website_clicks=30 + i,
        ))

    for i in range(3):
        _s.add(Post(
            client_id=_client.id,
            scheduled_at=date(2026, 5, 22 + i),
            format=PostFormat.IMAGE,
            status=PostStatus.PUBLICADO,
        ))

    _s.commit()
    _client_id = _client.id


# --- Tests de report_service ---

def test_generar_html_contiene_datos_cliente():
    from services.report_service import generar_reporte_html

    with Session(_engine) as session:
        html = generar_reporte_html(session, semanas_atras=1)

    assert "diavolo_lab" in html.lower() or "Diavolo Lab" in html
    assert "Impresiones" in html or "impressions" in html.lower()
    assert "<html" in html.lower()


def test_generar_html_incluye_posts_publicados():
    from services.report_service import generar_reporte_html

    with Session(_engine) as session:
        html = generar_reporte_html(session, semanas_atras=1)

    assert "Publicado" in html or "publicado" in html.lower()


def test_enviar_reporte_mock():
    from services.resend_service import enviar_reporte

    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {"id": "email_abc123"}

    with patch("services.resend_service.httpx.post", return_value=mock_resp):
        msg_id = enviar_reporte(
            to="equipo@diavolo.agency",
            subject="Reporte semanal",
            html="<h1>Test</h1>",
        )

    assert msg_id == "email_abc123"


def test_enviar_reporte_falla_sin_api_key(monkeypatch):
    from services.resend_service import enviar_reporte
    monkeypatch.delenv("RESEND_API_KEY", raising=False)

    with pytest.raises(RuntimeError, match="RESEND_API_KEY"):
        enviar_reporte("to@test.com", "Subject", "<p>HTML</p>")


@pytest.mark.asyncio
async def test_job_semanal_mock():
    from services.scheduler import enviar_reporte_semanal

    mock_html = "<html><body>Reporte</body></html>"
    mock_id = "email_mock_001"

    with patch("services.scheduler.generar_reporte_html", return_value=mock_html), \
         patch("services.scheduler.enviar_reporte", return_value=mock_id):
        await enviar_reporte_semanal(_engine)
