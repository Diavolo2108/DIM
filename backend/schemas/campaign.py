from datetime import datetime, date
from pydantic import BaseModel
from models.campaign import CampaignStatus


class PlanRequest(BaseModel):
    message: str
    historial: list[dict] = []
    contexto_cliente: str | None = None


class PlanResponse(BaseModel):
    respuesta: str
    historial_actualizado: list[dict]


class CampaignCreate(BaseModel):
    client_id: str
    name: str
    objetivo: str
    historial: list[dict] = []
    duracion_inicio: date | None = None
    duracion_fin: date | None = None


class CampaignOut(BaseModel):
    id: str
    client_id: str
    name: str
    objetivo: str
    status: CampaignStatus
    frecuencia: str | None = None
    tono: str | None = None
    hashtags: list | None = None
    duracion_inicio: date | None = None
    duracion_fin: date | None = None
    contexto_path: str | None = None
    aprobacion_path: str | None = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
