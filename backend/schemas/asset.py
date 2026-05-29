from datetime import datetime
from pydantic import BaseModel


class AssetOut(BaseModel):
    id: str
    client_id: str
    campaign_id: str | None = None
    post_id: str | None = None
    r2_url: str
    filename: str
    content_type: str
    size_bytes: int
    created_at: datetime

    model_config = {"from_attributes": True}
