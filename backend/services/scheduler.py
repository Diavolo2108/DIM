from datetime import datetime, timezone, timedelta

import os

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session

from models.asset import Asset
from models.client import Client
from models.post import Post, PostFormat, PostStatus
from services.encryption_service import decrypt, encrypt
from services.report_service import generar_reporte_html
from services.resend_service import enviar_reporte
from services.meta_service import (
    _build_caption_with_hashtags,
    create_carousel_container,
    create_carousel_item,
    create_image_container,
    create_reel_container,
    publish_container,
    refresh_long_lived_token,
)

MAX_RETRIES = 3

scheduler = AsyncIOScheduler()

# La engine se inyecta al inicializar el scheduler
_db_engine: Engine | None = None


async def publish_post(post: Post, client: Client, session: Session) -> None:
    """Publica un post en Instagram. Actualiza estado en BD."""
    token = decrypt(client.access_token_encrypted)
    account_id = client.instagram_account_id
    caption = _build_caption_with_hashtags(post.copy, post.hashtags)

    assets = session.query(Asset).filter_by(post_id=post.id).all()

    try:
        if post.format == PostFormat.IMAGE or (post.format == PostFormat.CAROUSEL and len(assets) <= 1):
            url = assets[0].r2_url if assets else ""
            container_id = create_image_container(account_id, token, url, caption)

        elif post.format == PostFormat.CAROUSEL:
            child_ids = [create_carousel_item(account_id, token, a.r2_url) for a in assets]
            container_id = create_carousel_container(account_id, token, child_ids, caption)

        elif post.format == PostFormat.REEL:
            url = assets[0].r2_url if assets else ""
            container_id = create_reel_container(account_id, token, url, caption)

        else:
            raise ValueError(f"Formato desconocido: {post.format}")

        media_id = publish_container(account_id, token, container_id)

        post.status = PostStatus.PUBLICADO
        post.instagram_media_id = media_id
        post.published_at = datetime.now(timezone.utc)

    except Exception as e:
        post.retry_count = (post.retry_count or 0) + 1
        if post.retry_count >= MAX_RETRIES:
            post.status = PostStatus.FALLIDO
            post.error_message = str(e)

    session.commit()


async def check_and_publish_posts(engine: Engine | None = None) -> None:
    """Busca posts vencidos y los publica. Llamado por APScheduler cada minuto."""
    eng = engine or _db_engine
    if not eng:
        return

    now = datetime.now(timezone.utc)
    with Session(eng) as session:
        posts_due = (
            session.query(Post)
            .filter(
                Post.status == PostStatus.PROGRAMADO,
                Post.scheduled_at <= now,
                Post.retry_count < MAX_RETRIES,
            )
            .all()
        )
        for post in posts_due:
            client = session.get(Client, post.client_id)
            if client:
                await publish_post(post, client, session)


DAYS_BEFORE_EXPIRY = 7  # rotar si quedan menos de 7 días


async def rotate_expiring_tokens(engine: Engine | None = None) -> None:
    """Renueva tokens de Meta próximos a vencer. Llamado diariamente por APScheduler."""
    eng = engine or _db_engine
    if not eng:
        return

    app_id = os.environ.get("META_APP_ID", "")
    app_secret = os.environ.get("META_APP_SECRET", "")
    if not app_id or not app_secret:
        return

    threshold = datetime.now(timezone.utc) + timedelta(days=DAYS_BEFORE_EXPIRY)

    with Session(eng) as session:
        expiring = (
            session.query(Client)
            .filter(
                Client.token_expires_at.isnot(None),
                Client.token_expires_at <= threshold,
                Client.status != "INACTIVA",
            )
            .all()
        )
        for client in expiring:
            try:
                current_token = decrypt(client.access_token_encrypted)
                new_token, expires_in = refresh_long_lived_token(current_token, app_id, app_secret)
                client.access_token_encrypted = encrypt(new_token)
                client.token_expires_at = datetime.now(timezone.utc) + timedelta(seconds=expires_in)
                session.commit()
            except Exception:
                pass  # Fallo silencioso; log en próxima revisión


def start_scheduler(engine: Engine) -> None:
    global _db_engine
    _db_engine = engine

    scheduler.add_job(
        check_and_publish_posts,
        trigger=IntervalTrigger(minutes=1),
        id="publish_due_posts",
        replace_existing=True,
    )
    scheduler.add_job(
        rotate_expiring_tokens,
        trigger=IntervalTrigger(hours=24),
        id="rotate_tokens",
        replace_existing=True,
    )
    scheduler.add_job(
        enviar_reporte_semanal,
        trigger="cron",
        day_of_week="mon",
        hour=9,
        minute=0,
        id="reporte_semanal",
        replace_existing=True,
    )
    if not scheduler.running:
        scheduler.start()


async def enviar_reporte_semanal(engine: Engine | None = None) -> None:
    """Genera y envía el reporte semanal de métricas a todos los clientes activos."""
    eng = engine or _db_engine
    if not eng:
        return

    to = os.environ.get("REPORT_EMAIL", "")
    if not to:
        return

    with Session(eng) as session:
        try:
            html = generar_reporte_html(session, semanas_atras=1)
            enviar_reporte(
                to=to,
                subject="📊 Reporte semanal — Diavolo Instagram Manager",
                html=html,
            )
        except Exception:
            pass  # Fallo silencioso; no interrumpe otros jobs
