from datetime import datetime
from pydantic import BaseModel
from models.client import ClientStatus


class ClientCreate(BaseModel):
    name: str
    instagram_username: str
    instagram_account_id: str
    access_token: str
    app_secret: str | None = None
    status: ClientStatus = ClientStatus.EN_PAUSA


class ClientUpdate(BaseModel):
    name: str | None = None
    instagram_username: str | None = None
    instagram_account_id: str | None = None
    access_token: str | None = None
    app_secret: str | None = None
    status: ClientStatus | None = None


class ClientOut(BaseModel):
    id: str
    name: str
    instagram_username: str
    instagram_account_id: str
    status: ClientStatus
    token_expires_at: datetime | None = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
