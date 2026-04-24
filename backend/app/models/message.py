"""Message model"""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Text, ForeignKey, Integer, Boolean
from sqlalchemy.orm import relationship
from app.database import Base


class Message(Base):
    """Individual message model"""
    __tablename__ = "messages"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    record_id = Column(String(36), ForeignKey("chat_records.id"), nullable=False, index=True)
    sender = Column(String(100), nullable=False)
    content = Column(Text, nullable=True)
    message_type = Column(String(20), default="text")  # text, image, voice, emoji, file
    timestamp = Column(DateTime, nullable=False, index=True)
    is_from_me = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    record = relationship("ChatRecord", back_populates="messages")