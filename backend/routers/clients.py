import os
from datetime import datetime, timezone, timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from database import get_db
from models.client import Client
from models.user import User
from routers.auth import _get_current_user
from schemas.client import ClientCreate, ClientUpdate, ClientOut
from services.encryption_service import encrypt, decrypt
from services.meta_service import refresh_long_lived_token

router = APIRouter(prefix="/clients", tags=["clients"])


@router.get("/", response_model=list[ClientOut])
def listar_clientes(
    db: Session = Depends(get_db),
    _: User = Depends(_get_current_user),
):
    return db.query(Client).order_by(Client.created_at.desc()).all()


@router.post("/", response_model=ClientOut, status_code=status.HTTP_201_CREATED)
def crear_cliente(
    body: ClientCreate,
    db: Session = Depends(get_db),
    _: User = Depends(_get_current_user),
):
    if db.query(Client).filter_by(instagram_username=body.instagram_username).first():
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Username ya registrado")

    token_expiry = datetime.now(timezone.utc) + timedelta(days=60)
    client = Client(
        name=body.name,
        instagram_username=body.instagram_username,
        instagram_account_id=body.instagram_account_id,
        access_token_encrypted=encrypt(body.access_token),
        app_secret_encrypted=encrypt(body.app_secret) if body.app_secret else None,
        status=body.status,
        token_expires_at=token_expiry,
    )
    db.add(client)
    db.commit()
    db.refresh(client)
    return client


@router.get("/{client_id}", response_model=ClientOut)
def obtener_cliente(
    client_id: str,
    db: Session = Depends(get_db),
    _: User = Depends(_get_current_user),
):
    client = db.get(Client, client_id)
    if not client:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cliente no encontrado")
    return client


@router.patch("/{client_id}", response_model=ClientOut)
def actualizar_cliente(
    client_id: str,
    body: ClientUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(_get_current_user),
):
    client = db.get(Client, client_id)
    if not client:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cliente no encontrado")

    if body.name is not None:
        client.name = body.name
    if body.instagram_username is not None:
        existing = db.query(Client).filter_by(instagram_username=body.instagram_username).first()
        if existing and existing.id != client_id:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Username ya registrado")
        client.instagram_username = body.instagram_username
    if body.instagram_account_id is not None:
        client.instagram_account_id = body.instagram_account_id
    if body.access_token is not None:
        client.access_token_encrypted = encrypt(body.access_token)
        client.token_expires_at = datetime.now(timezone.utc) + timedelta(days=60)
    if body.app_secret is not None:
        client.app_secret_encrypted = encrypt(body.app_secret)
    if body.status is not None:
        client.status = body.status

    db.commit()
    db.refresh(client)
    return client


@router.post("/{client_id}/refresh-token", response_model=ClientOut)
def refresh_token_manual(
    client_id: str,
    db: Session = Depends(get_db),
    _: User = Depends(_get_current_user),
):
    client = db.get(Client, client_id)
    if not client:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cliente no encontrado")

    app_id = os.environ.get("META_APP_ID", "")
    app_secret = os.environ.get("META_APP_SECRET", "")
    if not app_id or not app_secret:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                            detail="META_APP_ID o META_APP_SECRET no configurados")

    try:
        current_token = decrypt(client.access_token_encrypted)
        new_token, expires_in = refresh_long_lived_token(current_token, app_id, app_secret)  # noqa
        client.access_token_encrypted = encrypt(new_token)
        client.token_expires_at = datetime.now(timezone.utc) + timedelta(seconds=expires_in)
        db.commit()
        db.refresh(client)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(e))

    return client


@router.delete("/{client_id}", status_code=status.HTTP_204_NO_CONTENT)
def desactivar_cliente(
    client_id: str,
    db: Session = Depends(get_db),
    _: User = Depends(_get_current_user),
):
    client = db.get(Client, client_id)
    if not client:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cliente no encontrado")
    client.status = "INACTIVA"
    db.commit()
