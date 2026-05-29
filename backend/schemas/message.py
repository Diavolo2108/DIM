from datetime import datetime
from pydantic import BaseModel
from models.message import MessageType


class MessageOut(BaseModel):
    id: str
    client_id: str
    post_id: str | None = None
    instagram_thread_id: str
    instagram_message_id: str
    sender_id: str
    sender_username: str | None = None
    content: str
    type: MessageType
    is_from_page: bool
    replied: bool
    received_at: datetime
    created_at: datetime

    model_config = {"from_attributes": True}


class ReplyRequest(BaseModel):
    content: str


class SyncResponse(BaseModel):
    nuevos: int
    total: int
