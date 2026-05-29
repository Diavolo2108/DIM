from datetime import datetime
from pydantic import BaseModel


class AutoReplyCreate(BaseModel):
    is_active: bool = False
    system_prompt: str | None = None
    delay_seconds: int = 0


class AutoReplyOut(BaseModel):
    id: str
    client_id: str
    is_active: bool
    system_prompt: str | None = None
    delay_seconds: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
