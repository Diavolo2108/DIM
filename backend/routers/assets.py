from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from database import get_db
from models.asset import Asset
from models.client import Client
from models.user import User
from routers.auth import _get_current_user
from schemas.asset import AssetOut
from services.r2_service import TIPOS_PERMITIDOS, _build_key, upload_file, delete_file

router = APIRouter(prefix="/assets", tags=["assets"])

MAX_SIZE_BYTES = 100 * 1024 * 1024  # 100 MB


@router.post("/upload", response_model=AssetOut, status_code=status.HTTP_201_CREATED)
async def upload_asset(
    file: UploadFile = File(...),
    client_id: str = Form(...),
    campaign_id: str | None = Form(None),
    db: Session = Depends(get_db),
    _: User = Depends(_get_current_user),
):
    if file.content_type not in TIPOS_PERMITIDOS:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=f"Tipo de archivo no permitido: {file.content_type}",
        )

    client = db.get(Client, client_id)
    if not client:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cliente no encontrado")

    data = await file.read()
    if len(data) > MAX_SIZE_BYTES:
        raise HTTPException(status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, detail="Archivo mayor a 100 MB")

    key = _build_key(client.instagram_username, file.filename or "archivo")
    r2_url = upload_file(data, key, file.content_type)

    asset = Asset(
        client_id=client_id,
        campaign_id=campaign_id,
        r2_key=key,
        r2_url=r2_url,
        filename=file.filename or "archivo",
        content_type=file.content_type,
        size_bytes=len(data),
    )
    db.add(asset)
    db.commit()
    db.refresh(asset)
    return asset


@router.get("/", response_model=list[AssetOut])
def listar_assets(
    client_id: str | None = None,
    campaign_id: str | None = None,
    db: Session = Depends(get_db),
    _: User = Depends(_get_current_user),
):
    q = db.query(Asset)
    if client_id:
        q = q.filter(Asset.client_id == client_id)
    if campaign_id:
        q = q.filter(Asset.campaign_id == campaign_id)
    return q.order_by(Asset.created_at.desc()).all()


@router.delete("/{asset_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_asset(
    asset_id: str,
    db: Session = Depends(get_db),
    _: User = Depends(_get_current_user),
):
    asset = db.get(Asset, asset_id)
    if not asset:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Asset no encontrado")
    delete_file(asset.r2_key)
    db.delete(asset)
    db.commit()
