from datetime import datetime
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from database import get_db
from models.campaign import Campaign
from models.client import Client
from models.post import Post
from models.user import User
from routers.auth import _get_current_user
from schemas.post import GenerateCopyRequest, GenerateCopyResponse, PostCreate, PostOut, PostUpdate
from services.claude_service import generar_copy

router = APIRouter(prefix="/posts", tags=["posts"])


def _leer_contexto_campana(campaign: Campaign) -> str | None:
    if campaign.contexto_path:
        p = Path(campaign.contexto_path)
        if p.exists():
            return p.read_text(encoding="utf-8")
    # Fallback: construir contexto desde los campos de la campaña
    partes = [f"Objetivo: {campaign.objetivo}"]
    if campaign.tono:
        partes.append(f"Tono: {campaign.tono}")
    if campaign.frecuencia:
        partes.append(f"Frecuencia: {campaign.frecuencia}")
    if campaign.hashtags:
        partes.append(f"Hashtags de campaña: {', '.join(campaign.hashtags)}")
    return "\n".join(partes) if partes else None


@router.post("/generate-copy", response_model=GenerateCopyResponse)
def generate_copy(
    body: GenerateCopyRequest,
    db: Session = Depends(get_db),
    _: User = Depends(_get_current_user),
):
    campaign = db.get(Campaign, body.campaign_id)
    if not campaign:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Campaña no encontrada")

    try:
        contexto = _leer_contexto_campana(campaign)
        copy, hashtags = generar_copy(
            instruccion=body.instruccion,
            formato=body.formato.value,
            campaign_context=contexto,
        )
    except RuntimeError as e:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(e))

    return GenerateCopyResponse(caption=copy, hashtags=hashtags)


@router.post("/", response_model=PostOut, status_code=status.HTTP_201_CREATED)
def crear_post(
    body: PostCreate,
    db: Session = Depends(get_db),
    _: User = Depends(_get_current_user),
):
    if not db.get(Client, body.client_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cliente no encontrado")

    post = Post(
        client_id=body.client_id,
        campaign_id=body.campaign_id,
        scheduled_at=body.scheduled_at,
        format=body.format,
        copy=body.caption,
        hashtags=body.hashtags,
    )
    db.add(post)
    db.commit()
    db.refresh(post)
    return post


@router.get("/", response_model=list[PostOut])
def listar_posts(
    client_id: str | None = None,
    campaign_id: str | None = None,
    month: str | None = Query(
        None,
        pattern=r"^\d{4}-(?:0[1-9]|1[0-2])$",
        description="Filtro de mes en formato YYYY-MM",
    ),
    db: Session = Depends(get_db),
    _: User = Depends(_get_current_user),
):
    q = db.query(Post)
    if client_id:
        q = q.filter(Post.client_id == client_id)
    if campaign_id:
        q = q.filter(Post.campaign_id == campaign_id)
    if month:
        year, mon = int(month[:4]), int(month[5:])
        inicio = datetime(year, mon, 1)
        fin_mon = mon + 1 if mon < 12 else 1
        fin_year = year if mon < 12 else year + 1
        fin = datetime(fin_year, fin_mon, 1)
        q = q.filter(Post.scheduled_at >= inicio, Post.scheduled_at < fin)
    return q.order_by(Post.scheduled_at).all()


@router.patch("/{post_id}", response_model=PostOut)
def actualizar_post(
    post_id: str,
    body: PostUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(_get_current_user),
):
    post = db.get(Post, post_id)
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post no encontrado")
    for field, value in body.model_dump(exclude_none=True).items():
        orm_field = "copy" if field == "caption" else field
        setattr(post, orm_field, value)
    db.commit()
    db.refresh(post)
    return post
