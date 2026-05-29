from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from database import get_db
from models.campaign import Campaign
from models.client import Client
from models.user import User
from routers.auth import _get_current_user
from schemas.campaign import CampaignCreate, CampaignOut, PlanRequest, PlanResponse
from services.claude_service import planificar_campana
from services.campaign_service import guardar_documentos

router = APIRouter(prefix="/campaigns", tags=["campaigns"])


@router.post("/plan", response_model=PlanResponse)
def planificar(
    body: PlanRequest,
    db: Session = Depends(get_db),
    _: User = Depends(_get_current_user),
):
    historial = list(body.historial)
    historial.append({"role": "user", "content": body.message})

    try:
        respuesta = planificar_campana(historial=historial, contexto_cliente=body.contexto_cliente)
    except RuntimeError as e:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(e))

    historial.append({"role": "assistant", "content": respuesta})
    return PlanResponse(respuesta=respuesta, historial_actualizado=historial)


@router.post("/", response_model=CampaignOut, status_code=status.HTTP_201_CREATED)
def crear_campana(
    body: CampaignCreate,
    db: Session = Depends(get_db),
    _: User = Depends(_get_current_user),
):
    client = db.get(Client, body.client_id)
    if not client:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cliente no encontrado")

    contexto_path, aprobacion_path, datos = guardar_documentos(
        instagram_username=client.instagram_username,
        campaign_name=body.name,
        historial=body.historial,
    )

    campaign = Campaign(
        client_id=body.client_id,
        name=body.name,
        objetivo=body.objetivo or datos.get("objetivo", body.name),
        frecuencia=datos.get("frecuencia"),
        tono=datos.get("tono"),
        hashtags=datos.get("hashtags"),
        duracion_inicio=body.duracion_inicio,
        duracion_fin=body.duracion_fin,
        contexto_path=contexto_path,
        aprobacion_path=aprobacion_path,
    )
    db.add(campaign)
    db.commit()
    db.refresh(campaign)
    return campaign


@router.get("/", response_model=list[CampaignOut])
def listar_campanas(
    client_id: str | None = None,
    db: Session = Depends(get_db),
    _: User = Depends(_get_current_user),
):
    q = db.query(Campaign)
    if client_id:
        q = q.filter(Campaign.client_id == client_id)
    return q.order_by(Campaign.created_at.desc()).all()


@router.get("/{campaign_id}", response_model=CampaignOut)
def obtener_campana(
    campaign_id: str,
    db: Session = Depends(get_db),
    _: User = Depends(_get_current_user),
):
    campaign = db.get(Campaign, campaign_id)
    if not campaign:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Campaña no encontrada")
    return campaign
