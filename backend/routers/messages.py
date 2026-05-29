from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from database import get_db
from models.client import Client
from models.message import Message, MessageType
from models.user import User
from routers.auth import _get_current_user
from schemas.message import MessageOut, ReplyRequest, SyncResponse
from services.inbox_service import send_reply_to_message, sync_client_messages

router = APIRouter(prefix="/messages", tags=["messages"])


@router.get("/", response_model=list[MessageOut])
def listar_mensajes(
    client_id: str | None = None,
    type: MessageType | None = None,
    replied: bool | None = Query(None),
    db: Session = Depends(get_db),
    _: User = Depends(_get_current_user),
):
    q = db.query(Message)
    if client_id:
        q = q.filter(Message.client_id == client_id)
    if type:
        q = q.filter(Message.type == type)
    if replied is not None:
        q = q.filter(Message.replied == replied)
    return q.order_by(Message.received_at.desc()).all()


@router.post("/sync", response_model=SyncResponse)
def sync_mensajes(
    client_id: str,
    db: Session = Depends(get_db),
    _: User = Depends(_get_current_user),
):
    client = db.get(Client, client_id)
    if not client:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cliente no encontrado")

    try:
        nuevos = sync_client_messages(client, db)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(e))

    total = db.query(Message).filter_by(client_id=client_id).count()
    return SyncResponse(nuevos=nuevos, total=total)


@router.post("/{message_id}/reply", response_model=MessageOut)
def responder_mensaje(
    message_id: str,
    body: ReplyRequest,
    db: Session = Depends(get_db),
    _: User = Depends(_get_current_user),
):
    message = db.get(Message, message_id)
    if not message:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Mensaje no encontrado")

    client = db.get(Client, message.client_id)
    if not client:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cliente no encontrado")

    try:
        send_reply_to_message(message, body.content, client, db)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(e))

    db.refresh(message)
    return message
