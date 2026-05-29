from datetime import datetime
from pydantic import BaseModel, Field
from models.post import PostFormat, PostStatus


class PostCreate(BaseModel):
    client_id: str
    campaign_id: str | None = None
    scheduled_at: datetime
    format: PostFormat = PostFormat.IMAGE
    caption: str | None = None
    hashtags: list[str] | None = None


class PostUpdate(BaseModel):
    scheduled_at: datetime | None = None
    format: PostFormat | None = None
    caption: str | None = None
    hashtags: list[str] | None = None
    status: PostStatus | None = None


class PostOut(BaseModel):
    id: str
    client_id: str
    campaign_id: str | None = None
    scheduled_at: datetime
    published_at: datetime | None = None
    format: PostFormat
    # validation_alias='copy': lee del ORM (col. 'copy') pero serializa como 'caption'
    caption: str | None = Field(None, validation_alias="copy")
    hashtags: list | None = None
    status: PostStatus
    instagram_media_id: str | None = None
    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True,
        "populate_by_name": True,
    }


class GenerateCopyRequest(BaseModel):
    campaign_id: str
    instruccion: str
    formato: PostFormat = PostFormat.IMAGE


class GenerateCopyResponse(BaseModel):
    caption: str
    hashtags: list[str]
