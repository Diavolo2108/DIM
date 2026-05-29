import os
import pytest
from datetime import datetime, timezone, timedelta
from unittest.mock import patch, MagicMock, AsyncMock
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

os.environ.setdefault("ENCRYPTION_KEY", "Qwk0PQm6j0zLpUI0goHhaaurhc8-b3njkiEYYXI1QBk=")

from models.base import Base
from models.client import Client, ClientStatus
from models.post import Post, PostFormat, PostStatus
from models.asset import Asset
from services.encryption_service import encrypt
from services.meta_service import (
    _build_caption_with_hashtags,
    META_API_BASE,
)

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
        access_token_encrypted=encrypt("EAABsbCS_fake_token"),
        status=ClientStatus.EN_CAMPANA,
    )
    _s.add(_client)
    _s.flush()

    # Post vencido (scheduled 1 hora atrás)
    _post_due = Post(
        client_id=_client.id,
        scheduled_at=datetime.now(timezone.utc) - timedelta(hours=1),
        format=PostFormat.IMAGE,
        status=PostStatus.PROGRAMADO,
        copy="Caption de prueba",
        hashtags=["diseño", "agencia"],
    )
    # Post futuro (no debe publicarse)
    _post_future = Post(
        client_id=_client.id,
        scheduled_at=datetime.now(timezone.utc) + timedelta(hours=2),
        format=PostFormat.IMAGE,
        status=PostStatus.PROGRAMADO,
    )
    _s.add_all([_post_due, _post_future])
    _s.flush()

    _asset = Asset(
        client_id=_client.id,
        post_id=_post_due.id,
        r2_key="clientes/diavolo_lab/test.jpg",
        r2_url="https://r2.example.com/test.jpg",
        filename="test.jpg",
        content_type="image/jpeg",
        size_bytes=50000,
    )
    _s.add(_asset)
    _s.commit()
    _client_id = _client.id
    _post_due_id = _post_due.id
    _post_future_id = _post_future.id


# --- Tests de meta_service helpers ---

def test_build_caption_con_hashtags():
    result = _build_caption_with_hashtags("Caption de prueba", ["diseño", "agencia"])
    assert "Caption de prueba" in result
    assert "#diseño" in result
    assert "#agencia" in result


def test_build_caption_sin_hashtags():
    result = _build_caption_with_hashtags("Solo caption", [])
    assert result == "Solo caption"


def test_meta_api_base_formato():
    assert META_API_BASE.startswith("https://graph.facebook.com/v")


# --- Tests de publish_post ---

@pytest.mark.asyncio
async def test_publish_image_post_exitoso():
    from services.scheduler import publish_post

    mock_create = MagicMock(return_value="container_123")
    mock_publish = MagicMock(return_value="media_456")

    with Session(_engine) as session:
        post = session.get(Post, _post_due_id)
        client = session.get(Client, _client_id)

        with patch("services.scheduler.create_image_container", mock_create), \
             patch("services.scheduler.publish_container", mock_publish):
            await publish_post(post, client, session)

        session.refresh(post)
        assert post.status == PostStatus.PUBLICADO
        assert post.instagram_media_id == "media_456"


@pytest.mark.asyncio
async def test_publish_falla_incrementa_retry():
    from services.scheduler import publish_post

    with Session(_engine) as session:
        # Crear post extra para este test
        post = Post(
            client_id=_client_id,
            scheduled_at=datetime.now(timezone.utc) - timedelta(hours=1),
            format=PostFormat.IMAGE,
            status=PostStatus.PROGRAMADO,
        )
        session.add(post)
        session.flush()

        asset = Asset(
            client_id=_client_id, post_id=post.id,
            r2_key="k", r2_url="https://r2.example.com/x.jpg",
            filename="x.jpg", content_type="image/jpeg", size_bytes=100,
        )
        session.add(asset)
        session.commit()

        with patch("services.scheduler.create_image_container", side_effect=Exception("API error")):
            await publish_post(post, session.get(Client, _client_id), session)

        session.refresh(post)
        assert post.status == PostStatus.PROGRAMADO  # no marcado FALLIDO aún
        assert post.retry_count == 1


@pytest.mark.asyncio
async def test_publish_fallido_tras_3_intentos():
    from services.scheduler import publish_post

    with Session(_engine) as session:
        post = Post(
            client_id=_client_id,
            scheduled_at=datetime.now(timezone.utc) - timedelta(hours=1),
            format=PostFormat.IMAGE,
            status=PostStatus.PROGRAMADO,
            retry_count=2,  # ya falló 2 veces
        )
        session.add(post)
        session.flush()

        asset = Asset(
            client_id=_client_id, post_id=post.id,
            r2_key="k2", r2_url="https://r2.example.com/y.jpg",
            filename="y.jpg", content_type="image/jpeg", size_bytes=100,
        )
        session.add(asset)
        session.commit()

        with patch("services.scheduler.create_image_container", side_effect=Exception("API error")):
            await publish_post(post, session.get(Client, _client_id), session)

        session.refresh(post)
        assert post.status == PostStatus.FALLIDO


@pytest.mark.asyncio
async def test_check_posts_solo_publica_vencidos():
    from services.scheduler import check_and_publish_posts

    mock_publish = AsyncMock()
    with patch("services.scheduler.publish_post", mock_publish):
        await check_and_publish_posts(_engine)

    # El post futuro nunca debe procesarse; los vencidos sí
    called_ids = [call.args[0].id for call in mock_publish.call_args_list]
    assert _post_future_id not in called_ids
    assert len(called_ids) >= 1  # al menos un post vencido procesado
