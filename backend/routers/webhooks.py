import hashlib
import hmac
import json
import os
from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException, Query, Request, status
from sqlalchemy.orm import Session

from database import get_db
from fastapi import Depends
from models.client import Client
from models.message import Message, MessageType
from models.post import Post, PostStatus

router = APIRouter(prefix="/webhook", tags=["webhooks"])

VERIFY_TOKEN = os.environ.get("META_WEBHOOK_VERIFY_TOKEN", "diavolo_webhook_token")


def _verify_signature(payload: bytes, signature: str) -> bool:
    """Verifica la firma X-Hub-Signature-256 de Meta."""
    app_secret = os.environ.get("META_APP_SECRET", "")
    if not app_secret:
        return False
    expected = "sha256=" + hmac.new(
        app_secret.encode(), payload, hashlib.sha256
    ).hexdigest()  # hmac.new = hmac.HMAC constructor alias
    return hmac.compare_digest(expected, signature)


@router.get("/meta")
def verificar_webhook(
    hub_mode: str = Query(alias="hub.mode"),
    hub_verify_token: str = Query(alias="hub.verify_token"),
    hub_challenge: str = Query(alias="hub.challenge"),
):
    """Endpoint de verificación que Meta llama al configurar el webhook."""
    if hub_mode == "subscribe" and hub_verify_token == VERIFY_TOKEN:
        return int(hub_challenge)
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Token de verificación inválido")


@router.post("/meta")
async def recibir_evento(request: Request, db: Session = Depends(get_db)):
    """Recibe eventos de Meta en tiempo real."""
    payload = await request.body()

    # Verificar firma si está configurado el app_secret
    signature = request.headers.get("X-Hub-Signature-256", "")
    if os.environ.get("META_APP_SECRET") and not _verify_signature(payload, signature):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Firma inválida")

    try:
        data = json.loads(payload)
    except json.JSONDecodeError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Payload inválido")

    for entry in data.get("entry", []):
        # Eventos de mensajería (DMs)
        for messaging in entry.get("messaging", []):
            _procesar_dm(messaging, db)

        # Cambios de Instagram (comentarios, posts publicados)
        for change in entry.get("changes", []):
            _procesar_change(change, entry.get("id", ""), db)

    db.commit()
    return {"status": "ok"}


def _procesar_dm(event: dict, db: Session) -> None:
    """Guarda un DM recibido vía webhook."""
    msg = event.get("message", {})
    msg_id = msg.get("mid", "")
    if not msg_id:
        return
    if db.query(Message).filter_by(instagram_message_id=msg_id).first():
        return  # Duplicado

    sender_id = event.get("sender", {}).get("id", "")
    recipient_id = event.get("recipient", {}).get("id", "")
    client = db.query(Client).filter_by(instagram_account_id=recipient_id).first()
    if not client:
        return

    db.add(Message(
        client_id=client.id,
        instagram_thread_id=event.get("sender", {}).get("id", ""),
        instagram_message_id=msg_id,
        sender_id=sender_id,
        content=msg.get("text", ""),
        type=MessageType.DM,
        is_from_page=False,
        replied=False,
        received_at=datetime.now(timezone.utc),
    ))


def _procesar_change(change: dict, ig_account_id: str, db: Session) -> None:
    """Procesa cambios: post publicado, comentarios."""
    field = change.get("field", "")
    value = change.get("value", {})

    if field == "media" and value.get("media_product_type") == "POST":
        # Post publicado en Instagram — actualizar estado en BD
        ig_media_id = value.get("media_id", "")
        if ig_media_id:
            post = db.query(Post).filter_by(instagram_media_id=ig_media_id).first()
            if post:
                post.status = PostStatus.PUBLICADO
                post.published_at = datetime.now(timezone.utc)

    elif field == "comments":
        client = db.query(Client).filter_by(instagram_account_id=ig_account_id).first()
        if not client:
            return
        comment_id = value.get("id", "")
        if not comment_id or db.query(Message).filter_by(instagram_message_id=comment_id).first():
            return
        db.add(Message(
            client_id=client.id,
            instagram_thread_id=value.get("media", {}).get("id", comment_id),
            instagram_message_id=comment_id,
            sender_id=value.get("from", {}).get("id", ""),
            sender_username=value.get("from", {}).get("username"),
            content=value.get("text", ""),
            type=MessageType.COMMENT,
            is_from_page=False,
            replied=False,
            received_at=datetime.now(timezone.utc),
        ))
