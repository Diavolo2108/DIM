from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from database import get_db
from models.auto_reply import AutoReply
from models.client import Client
from models.user import User
from routers.auth import _get_current_user
from schemas.auto_reply import AutoReplyCreate, AutoReplyOut

router = APIRouter(prefix="/auto-replies", tags=["auto-replies"])


@router.get("/{client_id}", response_model=AutoReplyOut)
def obtener_auto_reply(
    client_id: str,
    db: Session = Depends(get_db),
    _: User = Depends(_get_current_user),
):
    ar = db.query(AutoReply).filter_by(client_id=client_id).first()
    if not ar:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Configuración no encontrada")
    return ar


@router.put("/{client_id}", response_model=AutoReplyOut)
def crear_o_actualizar_auto_reply(
    client_id: str,
    body: AutoReplyCreate,
    db: Session = Depends(get_db),
    _: User = Depends(_get_current_user),
):
    if not db.get(Client, client_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cliente no encontrado")

    ar = db.query(AutoReply).filter_by(client_id=client_id).first()
    if ar:
        ar.is_active = body.is_active
        ar.system_prompt = body.system_prompt
        ar.delay_seconds = body.delay_seconds
    else:
        ar = AutoReply(
            client_id=client_id,
            is_active=body.is_active,
            system_prompt=body.system_prompt,
            delay_seconds=body.delay_seconds,
        )
        db.add(ar)

    db.commit()
    db.refresh(ar)
    return ar


@router.patch("/{client_id}/toggle", response_model=AutoReplyOut)
def toggle_auto_reply(
    client_id: str,
    db: Session = Depends(get_db),
    _: User = Depends(_get_current_user),
):
    ar = db.query(AutoReply).filter_by(client_id=client_id).first()
    if not ar:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Configuración no encontrada")
    ar.is_active = not ar.is_active
    db.commit()
    db.refresh(ar)
    return ar
