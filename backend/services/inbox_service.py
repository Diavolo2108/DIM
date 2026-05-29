from datetime import datetime, timezone

from sqlalchemy.orm import Session

from models.auto_reply import AutoReply
from models.client import Client
from models.message import Message, MessageType
from services.claude_service import get_client
from services.encryption_service import decrypt
from services.meta_service import (
    get_instagram_conversations,
    send_dm_reply,
    reply_to_comment,
)

AUTO_REPLY_SYSTEM = """Eres el asistente de atención al cliente de esta cuenta de Instagram.
Responde de forma amable, profesional y concisa (máximo 3 oraciones).
Si el cliente hace una pregunta técnica o necesita información específica, indícale que un miembro del equipo le responderá pronto.
Idioma: responde en el mismo idioma que el cliente."""


def _generar_autorrespuesta(system_prompt: str | None, message_content: str) -> str:
    """Genera una respuesta automática con Claude."""
    client = get_client()
    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=256,
        system=system_prompt or AUTO_REPLY_SYSTEM,
        messages=[{"role": "user", "content": message_content}],
    )
    return response.content[0].text.strip()


def sync_client_messages(client: Client, db: Session) -> int:
    """Sincroniza DMs desde Meta para un cliente. Devuelve cantidad de mensajes nuevos."""
    token = decrypt(client.access_token_encrypted)
    account_id = client.instagram_account_id
    nuevos = 0

    conversations = get_instagram_conversations(account_id, token)

    for conv in conversations:
        messages_data = conv.get("messages", {}).get("data", [])
        for msg in messages_data:
            msg_id = msg.get("id", "")
            if not msg_id:
                continue
            if db.query(Message).filter_by(instagram_message_id=msg_id).first():
                continue  # ya existe

            sender = msg.get("from", {})
            is_from_page = sender.get("id") == account_id

            created_raw = msg.get("created_time", "")
            try:
                received_at = datetime.fromisoformat(created_raw.replace("+0000", "+00:00"))
            except (ValueError, AttributeError):
                received_at = datetime.now(timezone.utc)

            message = Message(
                client_id=client.id,
                instagram_thread_id=conv["id"],
                instagram_message_id=msg_id,
                sender_id=sender.get("id", ""),
                sender_username=sender.get("name"),
                content=msg.get("message", ""),
                type=MessageType.DM,
                is_from_page=is_from_page,
                replied=False,
                received_at=received_at,
            )
            db.add(message)
            nuevos += 1

    db.commit()

    # Autorrespuesta automática para nuevos DMs entrantes
    if nuevos > 0:
        ar = db.query(AutoReply).filter_by(client_id=client.id, is_active=True).first()
        if ar:
            token = decrypt(client.access_token_encrypted)
            nuevos_msgs = (
                db.query(Message)
                .filter_by(client_id=client.id, type=MessageType.DM, is_from_page=False, replied=False)
                .all()
            )
            for msg in nuevos_msgs:
                try:
                    respuesta = _generar_autorrespuesta(ar.system_prompt, msg.content)
                    reply_id = send_dm_reply(client.instagram_account_id, token, msg.sender_id, respuesta)
                    msg.replied = True
                    reply_record = Message(
                        client_id=client.id,
                        instagram_thread_id=msg.instagram_thread_id,
                        instagram_message_id=reply_id or f"auto_{msg.instagram_message_id}",
                        sender_id=client.instagram_account_id,
                        content=respuesta,
                        type=MessageType.DM,
                        is_from_page=True,
                        replied=False,
                        received_at=datetime.now(timezone.utc),
                    )
                    db.add(reply_record)
                except Exception:
                    pass  # Fallo silencioso en autorrespuesta, no bloquea el sync
            db.commit()

    return nuevos


def send_reply_to_message(message: Message, reply_text: str, client: Client, db: Session) -> str:
    """Responde a un DM o comentario y lo registra en BD."""
    token = decrypt(client.access_token_encrypted)
    account_id = client.instagram_account_id

    if message.type == MessageType.DM:
        reply_id = send_dm_reply(account_id, token, message.sender_id, reply_text)
    else:
        reply_id = reply_to_comment(message.instagram_message_id, token, reply_text)

    message.replied = True

    # Guardar la respuesta enviada como mensaje nuevo
    reply_msg = Message(
        client_id=message.client_id,
        instagram_thread_id=message.instagram_thread_id,
        instagram_message_id=reply_id or f"reply_{message.instagram_message_id}",
        sender_id=account_id,
        content=reply_text,
        type=message.type,
        is_from_page=True,
        replied=False,
        received_at=datetime.now(timezone.utc),
    )
    db.add(reply_msg)
    db.commit()
    return reply_id
