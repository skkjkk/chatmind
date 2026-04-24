"""Chat record schemas"""
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


# Request schemas
class ChatRecordCreate(BaseModel):
    contact_name: str = Field(..., min_length=1, max_length=100)


class ChatRecordUpdate(BaseModel):
    contact_name: Optional[str] = Field(None, min_length=1, max_length=100)


# Response schemas
class MessageDetail(BaseModel):
    id: str
    sender: str
    content: Optional[str]
    message_type: str
    timestamp: datetime
    is_from_me: bool

    class Config:
        from_attributes = True


class ChatRecordResponse(BaseModel):
    id: str
    user_id: str
    contact_name: str
    file_name: Optional[str]
    message_count: int
    parse_status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ChatRecordDetailResponse(ChatRecordResponse):
    messages: list[MessageDetail] = []

    class Config:
        from_attributes = True


class ChatRecordListResponse(BaseModel):
    records: list[ChatRecordResponse]
    total: int